from fastapi import APIRouter, HTTPException
from app.facade.facade import PokemonFacade
from app.facade.facade import PokemonFacade
from models.models import PokemonResponseModel, VerfifiedModel
import logging

router = APIRouter(prefix="/pokemon", tags=["pokemon"])
logger = logging.getLogger(__name__)

pokemon_facade = PokemonFacade()

@router.get("/random", response_model=PokemonResponseModel)
async def get_random_pokemon() -> PokemonResponseModel:
    try:
        pokemon = pokemon_facade.get_random_pokemon()
        answers = pokemon_facade.generate_answers(pokemon)
        base_image = pokemon_facade.get_pokemon_image(
            pokemon["sprites"]["other"]["official-artwork"]["front_default"]
        )
        silhouette = pokemon_facade.create_silhouette(img_bytes=base_image)
        
        return PokemonResponseModel(
            id=pokemon["id"],
            silhouette=silhouette,
            answers=answers
        )
    except Exception as e:
        logger.error(f"Error getting random pokemon: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify", response_model=VerfifiedModel)
async def verify_answer(
    pokemon_id: int,
    pokemon_answer_name: str,
) -> VerfifiedModel:
    try:
        correct_pokemon = pokemon_facade.verify_answer(pokemon_id=pokemon_id)
        correct_pokemon_name = correct_pokemon["name"]
        is_correct = pokemon_answer_name.lower() == correct_pokemon_name.lower()
        
        image = pokemon_facade.get_pokemon_image(
            correct_pokemon["sprites"]["other"]["official-artwork"]["front_default"]
        )
        encoded_image = pokemon_facade.encode_image_base64(img=image)
        
        return VerfifiedModel(
            name=correct_pokemon_name,
            image=encoded_image,
            is_correct=is_correct
        )
    except Exception as e:
        logger.error(f"Error verifying answer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"Pokemon not found: {e}")