from datetime import datetime
from fastapi import FastAPI, Depends
from database import get_session
from models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel,ConfigDict
from pwdlib import PasswordHash

app = FastAPI()

password_hash = PasswordHash.recommended()

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

@app.get("/")
def hello():
    return {"message": "ok"}

@app.post("/users", response_model=UserResponse)
def create_user(body: CreateUserRequest, session: Session = Depends(get_session)) -> UserResponse:
    # パスワードはハッシュ化する
    password = body.password
    hash = password_hash.hash(password)
    user = User(
        # exclude で指定した内容だけ除外できる
        **body.model_dump(exclude={"password"}),
        password=hash
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_session)) -> list[UserResponse]:
    statement = select(User)
    result = session.scalars(statement).all()
    return result

