import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_session
from app.models import User

# Authorization ヘッダーから Bearer トークンを取り出す
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    access_token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    """access_token を検証し、ユーザー情報を返却する。"""

    try:
        # access_token をデコード
        decoded = jwt.decode(
            access_token, key=settings.secret, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの有効期限が切れました",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの形式が正しくありません",
        )

    # access_token 以外の場合はエラーとする
    if decoded.get("type") != "access":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの種別が正しくありません",
        )

    # sub の検証
    sub = decoded.get("sub")
    if sub is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました")

    # ユーザーを検索し、認証成功した場合はそのユーザーを返却する
    user_id: int = int(sub)
    user: User = session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました")

    return user
