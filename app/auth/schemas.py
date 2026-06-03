from pydantic import BaseModel, ConfigDict


class SignupUserRequest(BaseModel):
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
