import jwt

from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
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

class LoginUserRequest(BaseModel):
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

@app.post("/login")
def login(body: LoginUserRequest, session: Session = Depends(get_session)):
    # まずはログイン情報を検証
    statement = select(User).where(User.name == body.name)
    user = session.scalars(statement).one_or_none()

    # ユーザーが存在しない場合は 404 エラー
    # 本番ではこのエラーを出すとユーザーの存在が確認できてしまうので、401 にまとめるのがよさそう
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="ユーザーが存在しません"
        )

    # ユーザーが存在する場合、パスワードのチェック
    is_verify = password_hash.verify(body.password, user.password)
    if not is_verify:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="ログイン情報が正しくありません"
        )
    return {"login": "ok"}
