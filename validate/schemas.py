from pydantic import EmailStr, BaseModel, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length= 72)