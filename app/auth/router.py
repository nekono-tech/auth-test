from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import LoginUserRequest, RefreshRequest, TokenResponse
from app.auth.security import password_hash
from app.auth.service import _create_token, refresh_token_verify
from app.db.session import get_session
from app.models import User
from app.users.schemas import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.post("/token/refresh", response_model=TokenResponse)
def token_refresh(body: RefreshRequest, session: Session = Depends(get_session)):
    # リフレッシュトークンを検証
    decoded = refresh_token_verify(body.refresh_token)

    # sub の検証
    sub = decoded.get("sub")
    if sub is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました")

    user: User = session.get(User, int(sub))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました")

    # トークンを再発行
    new_access_token = _create_token(user.id, "access", timedelta(minutes=5))
    new_refresh_token = _create_token(user.id, "refresh", timedelta(minutes=10))

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@router.post("/login")
def login(body: LoginUserRequest, session: Session = Depends(get_session)):
    # まずはログイン情報を検証
    statement = select(User).where(User.name == body.name)
    user = session.scalars(statement).one_or_none()

    # ユーザーが存在しない場合は 404 エラー
    # 本番ではこのエラーを出すとユーザーの存在が確認できてしまうので、401 にまとめるのがよさそう
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="ユーザーが存在しません")

    # ユーザーが存在する場合、パスワードのチェック
    is_verify = password_hash.verify(body.password, user.password)
    if not is_verify:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="ログイン情報が正しくありません"
        )

    # トークン生成
    access_token = _create_token(user.id, "access", timedelta(minutes=5))
    refresh_token = _create_token(user.id, "refresh", timedelta(minutes=10))

    return {"access_token": access_token, "refresh_token": refresh_token}
