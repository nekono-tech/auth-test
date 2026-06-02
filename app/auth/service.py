from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.config import settings


def _create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        # パスワードを含めないサブジェクト情報
        "sub": str(user_id),
        # トークン種別
        "type": token_type,
        # 有効期限
        "exp": datetime.now(tz=UTC) + expires_delta,
    }

    return jwt.encode(
        payload=payload, key=settings.secret, algorithm=settings.algorithm
    )


def refresh_token_verify(refresh_token: str):
    """リフレッシュトークンを検証し、デコード結果を返却する。"""
    try:
        # refresh_token をデコード
        decoded = jwt.decode(
            refresh_token, key=settings.secret, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの有効期限が切れました",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの形式が正しくありません",
        )

    # refresh_token 以外の場合はエラーとする
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの種別が正しくありません",
        )

    return decoded
