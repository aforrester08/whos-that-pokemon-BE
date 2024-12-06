import pytest
from unittest.mock import Mock, patch
from app.facade.facade import PokemonFacade

@pytest.fixture
def mock_pokeapi_client():
    client_mock = Mock()
    return client_mock

@pytest.fixture
def pokemon_facade(mock_pokeapi_client):
    with patch('app.facade.facade.PokeApiClient', return_value=mock_pokeapi_client):
        return PokemonFacade()

def test_get_random_pokemon(pokemon_facade, mock_pokeapi_client):
    expected_pokemon = {"id": 25, "name": "pikachu"}
    mock_pokeapi_client.get_random_pokemon.return_value = expected_pokemon
    
    result = pokemon_facade.get_random_pokemon()
    
    assert result == expected_pokemon
    mock_pokeapi_client.get_random_pokemon.assert_called_once()

def test_generate_answers(pokemon_facade, mock_pokeapi_client):
    correct_pokemon = {"id": 25, "name": "pikachu"}
    random_pokemon1 = {"id": 1, "name": "bulbasaur"}
    random_pokemon2 = {"id": 4, "name": "charmander"}
    random_pokemon3 = {"id": 7, "name": "squirtle"}
    
    mock_pokeapi_client.get_random_pokemon.side_effect = [
        random_pokemon1, 
        random_pokemon2, 
        random_pokemon3
    ]
    
    with patch('random.shuffle') as mock_shuffle:
        answers = pokemon_facade.generate_answers(correct_pokemon)
        
        assert len(answers) == 4
        assert correct_pokemon["name"] in answers
        mock_pokeapi_client.get_random_pokemon.call_count == 3
        mock_shuffle.assert_called_once()

def test_verify_answer(pokemon_facade, mock_pokeapi_client):
    pokemon_id = 25
    expected_pokemon = {"id": 25, "name": "pikachu"}
    mock_pokeapi_client.get_pokemon_by_id.return_value = expected_pokemon

    result = pokemon_facade.verify_answer(pokemon_id)
    
    assert result == expected_pokemon
    mock_pokeapi_client.get_pokemon_by_id.assert_called_once_with(pokemon_id)
