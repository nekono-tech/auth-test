from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_session
from app.models import User
from app.auth.security import password_hash
from app.users.schemas import CreateUserRequest, UserResponse

router = APIRouter()


@router.post("/users", response_model=UserResponse)
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


@router.get("/users", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_session)) -> list[UserResponse]:
    statement = select(User)
    result = session.scalars(statement).all()
    return result
