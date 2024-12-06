import pytest
from unittest.mock import Mock, patch
import time
import requests
from typing import Dict, Any

from app.client.client import (
    PokeApiClient,
    PokeApiError,
    RateLimitExceeded
)

# Fixtures
@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """Sample Pokemon data for testing"""
    return {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "base_experience": 64
    }

@pytest.fixture
def client():
    """Create a PokeApiClient instance with test settings"""
    return PokeApiClient(
        url="https://test.pokeapi.co/api/v2",
        rate_limit=2,
        rate_limit_period=1
    )

# Basic Functionality Tests
def test_init_default_values():
    """Test client initialization with default values"""
    client = PokeApiClient()
    assert client.url == "https://pokeapi.co/api/v2"
    assert client._rate_limit == 100
    assert client._rate_limit_period == 60

def test_init_custom_values():
    """Test client initialization with custom values"""
    client = PokeApiClient(
        url="https://custom.api",
        rate_limit=50,
        rate_limit_period=30
    )
    assert client.url == "https://custom.api"
    assert client._rate_limit == 50
    assert client._rate_limit_period == 30

# Rate Limiting Tests
def test_rate_limit_exceeded():
    """Test rate limit enforcement"""
    client = PokeApiClient(rate_limit=2, rate_limit_period=1)
    
    # Add timestamps just under the limit
    client._request_timestamps = [time.time() for _ in range(2)]
    
    with pytest.raises(RateLimitExceeded):
        client._check_rate_limit()

def test_rate_limit_cleanup():
    """Test cleanup of old timestamps"""
    client = PokeApiClient(rate_limit=2, rate_limit_period=1)
    
    # Add old timestamp
    client._request_timestamps = [time.time() - 2]  # 2 seconds old
    client._check_rate_limit()  # Should clean up old timestamp
    
    assert len(client._request_timestamps) == 0

# API Request Tests
@patch('requests.Session.get')
def test_successful_request(mock_get, client, mock_response):
    """Test successful API request"""
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    
    response = client.get_pokemon_by_id(1)
    
    assert response == mock_response
    mock_get.assert_called_once_with(
        url='https://test.pokeapi.co/api/v2/pokemon/1',
        timeout=5,
        headers={'User-Agent': 'PokeAPI-Client/1.0'}
    )

@patch('requests.Session.get')
def test_timeout_handling(mock_get, client):
    """Test handling of request timeout"""
    mock_get.side_effect = requests.exceptions.Timeout
    
    with pytest.raises(PokeApiError, match="Request timed out"):
        client.get_pokemon_by_id(1)

@patch('requests.Session.get')
def test_connection_error_handling(mock_get, client):
    """Test handling of connection error"""
    mock_get.side_effect = requests.exceptions.ConnectionError
    
    with pytest.raises(PokeApiError, match="Failed to connect to PokeAPI"):
        client.get_pokemon_by_id(1)

@patch('requests.Session.get')
def test_http_error_handling(mock_get, client):
    """Test handling of HTTP error"""
    mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error")
    
    with pytest.raises(PokeApiError, match="HTTP error"):
        client.get_pokemon_by_id(1)

# Input Validation Tests
def test_invalid_pokemon_id(client):
    """Test validation of Pokemon ID"""
    with pytest.raises(ValueError, match="Pokemon ID must be a positive integer"):
        client.get_pokemon_by_id(-1)
    
    with pytest.raises(ValueError, match="Pokemon ID must be a positive integer"):
        client.get_pokemon_by_id(0)

def test_invalid_max_pokemon_id(client):
    """Test validation of maximum Pokemon ID"""
    with pytest.raises(ValueError, match="Maximum Pokemon ID must be a positive integer"):
        client.get_random_pokemon(0)

# Caching Tests
@patch('requests.Session.get')
def test_caching_behavior(mock_get, client, mock_response):
    """Test that caching works correctly"""
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    
    # First call should make a request
    first_response = client.get_pokemon_by_id(1)
    # Second call should use cache
    second_response = client.get_pokemon_by_id(1)
    
    assert first_response == second_response
    mock_get.assert_called_once()  # Should only be called once due to caching

@patch('requests.Session.get')
def test_cache_clearing(mock_get, client, mock_response):
    """Test cache clearing functionality"""
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    
    # Make initial request
    client.get_pokemon_by_id(1)
    # Clear cache
    client.clear_cache()
    # Make same request again
    client.get_pokemon_by_id(1)
    
    assert mock_get.call_count == 2  # Should be called twice due to cache clearing

# Random Pokemon Tests
@patch('random.randint')
@patch('requests.Session.get')
def test_get_random_pokemon(mock_get, mock_randint, client, mock_response):
    """Test random Pokemon selection"""
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    mock_randint.return_value = 1
    
    response = client.get_random_pokemon(max_pokemon_id=898)
    
    assert response == mock_response
    mock_randint.assert_called_once_with(1, 898)

def test_logging_setup(caplog, client):
    with patch('requests.Session.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout
        
        with pytest.raises(PokeApiError):
            client.get_pokemon_by_id(1)
        
        assert "Request to https://test.pokeapi.co/api/v2/pokemon/1 timed out" in caplog.text