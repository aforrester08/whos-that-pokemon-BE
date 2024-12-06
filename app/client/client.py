import random
from typing import Dict, Any, Optional
import requests
import os
from dotenv import load_dotenv
import logging
import time
from functools import lru_cache


class PokeApiError(Exception):
    """Custom exception for PokeAPI-related errors"""
    pass

class RateLimitExceeded(PokeApiError):
    """Raised when API rate limit is exceeded"""
    pass

class PokeApiClient:
    def __init__(
        self,
        url: Optional[str] = None,
        cache_ttl: int = 3600,
        rate_limit: int = 100,
        rate_limit_period: int = 60
    ):
        load_dotenv()
        
        self.url = url or os.getenv("POKEAPI_URL", "https://pokeapi.co/api/v2")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        self._rate_limit = rate_limit
        self._rate_limit_period = rate_limit_period
        self._request_timestamps: list[float] = []

    def _check_rate_limit(self) -> None:
        current_time = time.time()
        self._request_timestamps = [
            ts for ts in self._request_timestamps
            if current_time - ts <= self._rate_limit_period
        ]
        
        if len(self._request_timestamps) >= self._rate_limit:
            raise RateLimitExceeded(
                f"Rate limit of {self._rate_limit} requests per {self._rate_limit_period} seconds exceeded"
            )

    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        self._check_rate_limit()
        
        try:
            self._request_timestamps.append(time.time())
            response = self.session.get(
                url=endpoint,
                timeout=5,
                headers={'User-Agent': 'PokeAPI-Client/1.0'}
            )
            
            if response.status_code == 429:
                raise RateLimitExceeded("PokeAPI rate limit exceeded")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise PokeApiError("Request timed out")
            
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while accessing {endpoint}")
            raise PokeApiError("Failed to connect to PokeAPI")
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            raise PokeApiError(f"HTTP error: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
            raise PokeApiError(f"Unexpected error: {e}")

    @lru_cache(maxsize=1000)
    def get_pokemon_by_id(self, pokemon_id: int) -> Dict[str, Any]:
        if not isinstance(pokemon_id, int) or pokemon_id < 1:
            raise ValueError("Pokemon ID must be a positive integer")
        
        endpoint = f"{self.url}/pokemon/{pokemon_id}"
        return self._make_request(endpoint)

    def get_random_pokemon(self, max_pokemon_id: int = 898) -> Dict[str, Any]:
        if not isinstance(max_pokemon_id, int) or max_pokemon_id < 1:
            raise ValueError("Maximum Pokemon ID must be a positive integer")
        
        random_id = random.randint(1, max_pokemon_id)
        return self.get_pokemon_by_id(random_id)

    def clear_cache(self) -> None:
        self.get_pokemon_by_id.cache_clear()
        self.logger.info("Cache cleared")
