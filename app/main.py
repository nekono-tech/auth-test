import jwt
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import get_session
from app.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from pwdlib import PasswordHash
from app.core.config import settings
from app.schemas.schema import CreateUserRequest, LoginUserRequest, TokenResponse, UserResponse, RefreshRequest

app = FastAPI()

# Authorization ヘッダーから Bearer トークンを取り出す
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hash = PasswordHash.recommended()

def get_current_user(
        access_token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
    ):
    """access_token を検証し、ユーザー情報を返却する。"""

    try:
        # access_token をデコード
        decoded = jwt.decode(
            access_token,
            key=settings.secret,
            algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの有効期限が切れました"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの形式が正しくありません"
        )
    
    # access_token 以外の場合はエラーとする
    if decoded.get("type") != "access":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="アクセストークンの種別が正しくありません"
        )

    # sub の検証
    sub = decoded.get("sub")
    if sub is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        )

    # ユーザーを検索し、認証成功した場合はそのユーザーを返却する
    user_id: int = int(sub)
    user: User = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        )
    
    return user


@app.get("/api/me", response_model=UserResponse)
def hello(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user

@app.post("/api/token/refresh", response_model=TokenResponse)
def token_refresh(body: RefreshRequest, session: Session = Depends(get_session)):
    # リフレッシュトークンを検証
    decoded = refresh_token_verify(body.refresh_token)

    # sub の検証
    sub = decoded.get("sub")
    if sub is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        )
    
    user: User = session.get(User, int(sub))
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        )

    # トークンを再発行
    new_access_token = _create_token(user.id, "access", timedelta(minutes=5))
    new_refresh_token = _create_token(user.id, "refresh", timedelta(minutes=10))

    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token
    }

def refresh_token_verify(refresh_token: str):
    """リフレッシュトークンを検証し、デコード結果を返却する。
    """
    try:
        # refresh_token をデコード
        decoded = jwt.decode(
            refresh_token,
            key=settings.secret,
            algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの有効期限が切れました"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの形式が正しくありません"
        )
    
    # refresh_token 以外の場合はエラーとする
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの種別が正しくありません"
        )
    
    return decoded


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

    # トークン生成
    access_token = _create_token(user.id, "access", timedelta(minutes=5))
    refresh_token = _create_token(user.id, "refresh", timedelta(minutes=10))

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token
    }


def _create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        # パスワードを含めないサブジェクト情報
        "sub": str(user_id),
        # トークン種別
        "type": token_type,
        # 有効期限
        "exp": datetime.now(tz=timezone.utc) + expires_delta
    }

    return jwt.encode(
        payload=payload,
        key=settings.secret,
        algorithm=settings.algorithm
    )
