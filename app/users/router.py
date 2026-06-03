from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models import User
from app.users.schemas import UserResponse

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_session)) -> list[UserResponse]:
    statement = select(User)
    result = session.scalars(statement).all()
    return result
