from pydantic import BaseModel,ConfigDict
from datetime import datetime

class CreateUserRequest(BaseModel):
    name: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class LoginUserRequest(BaseModel):
    name: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
