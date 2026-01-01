from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.functional_validators import field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("password")
    @classmethod
    def password_must_be_valid_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"