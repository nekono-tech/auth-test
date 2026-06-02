from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateUserRequest(BaseModel):
    name: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
