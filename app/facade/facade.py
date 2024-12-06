import logging
import random
from app.client.client import PokeApiClient
from app.utils.image_proccessing import ImageProcessing
import requests


class PokemonFacade:
    def __init__(self):
        self._pokeapi_client = PokeApiClient(
            cache_ttl=1800,
            rate_limit=50,
            rate_limit_period=60
        )
        self._image_processing = ImageProcessing()
        self.logger = logging.getLogger(__name__)
        
    def get_random_pokemon(self):
        self.logger.info("retrieving random pokemon")
        return self._pokeapi_client.get_random_pokemon()

    def generate_answers(self, correct_answer):
        self.logger.info("retrieving randomised answer options")
        answers = [self._pokeapi_client.get_random_pokemon()["name"] for i in range(3)]
        answers.append(correct_answer["name"])
        random.shuffle(answers)
        return answers
    
    def verify_answer(self, pokemon_id: int):
        self.logger.info("verifying answer")
        return self._pokeapi_client.get_pokemon_by_id(pokemon_id)
    
    def get_pokemon_image(self, image_url):
        self.logger.info("retrieving image from pokeapi")
        response = requests.get(image_url)
        return response.content
    
    def create_silhouette(self, img_bytes: bytes):
        self.logger.info("creating silhoutte")
        return self._image_processing.create_silhouette(img_bytes=img_bytes)
    
    def encode_image_base64(self, img):
        self.logger.info("encoding image")
        return self._image_processing.encode_image_base64(img=img)

