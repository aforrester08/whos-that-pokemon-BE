from pydantic import BaseModel


class PokemonResponseModel(BaseModel):
    id: str
    silhouette: str
    answers: list[str]

class VerfifiedModel(BaseModel):
    name: str
    image: str
    is_correct: bool