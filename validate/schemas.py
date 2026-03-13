from pydantic import EmailStr, BaseModel, Field
from typing import List

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length= 72)

class Pokemon(BaseModel):
    pokemons: List[str]