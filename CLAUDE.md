# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

JWT 認証を学習・検証するための FastAPI アプリ。ユーザー登録、ログイン、アクセス/リフレッシュトークンの発行・検証・再発行を行う。永続化は SQLAlchemy + SQLite (`test.db`)、マイグレーションは Alembic。パッケージ管理は uv (Python >= 3.14)。

コメント・エラーメッセージは日本語で書かれているため、新規コードも日本語コメントで揃える。

## Commands

```sh
fastapi dev                 # 開発サーバー起動 (ホットリロード、http://127.0.0.1:8000、/docs に Swagger UI)
uv sync                     # 依存関係のインストール
uv add <package>            # 依存追加

alembic upgrade head        # マイグレーション適用
alembic revision --autogenerate -m "message"   # モデル変更からマイグレーション自動生成
alembic downgrade -1        # 1 つ戻す
```

テストフレームワークやリンターは未導入。

## Architecture

ドメイン分割型(`auth` / `users`)+ DB レイヤー分離の構成。リクエストは各ドメインの `router.py` に入り、`Depends(get_session)` で DB セッション、`Depends(get_current_user)` で認証済みユーザーを注入する。

- `app/main.py` — `FastAPI()` インスタンスと `include_router` のみ。ロジックは持たない。
- `app/auth/` — 認証ドメイン。`router.py`(`router = APIRouter(prefix="/auth")`。`/signup`, `/login`, `/me`, `/token/refresh`)、`service.py`(`_create_token`, `refresh_token_verify`)、`dependencies.py`(`oauth2_scheme`, `get_current_user`)、`security.py`(`password_hash`)、`schemas.py`(`SignupUserRequest`, `LoginUserRequest`, `RefreshRequest`, `TokenResponse`)。ユーザー登録(signup)は「資格情報(パスワード)を発行する認証操作」として users ではなく auth に置く。そのため signup は `password_hash` でハッシュ化し、`app.models.User` へ直接 add/commit する。
- `app/users/` — ユーザードメイン。`router.py`(`/users` list のみ)、`schemas.py`(`UserResponse`)。参照系に徹し、auth への越境 import は持たない。
- `app/config.py` — `pydantic-settings` の `Settings`。`.env` から `secret`(JWT 署名鍵)と `algorithm` を読み込み、`settings` シングルトンとして公開。鍵へのアクセスはこれ経由のみ。
- `app/db/` — DB レイヤー。`base_class.py`(**`Base` の正本** = `DeclarativeBase` と `TimestampMixin`)、`session.py`(engine / `SessionLocal` / `get_session` / `DATABASE_URL`)、`base.py`(Alembic 用に `Base` + 全モデルを import する集約ファイル)。
- `app/models.py` — SQLAlchemy ORM モデル。`User` テーブル名は `auth_user`、`name` は unique。`Base` は `app.db.base_class` から継承する。

### トークン規約

`app/auth/service.py` の `_create_token()` がトークン生成の単一の入口で、payload に `sub`(user id)・`type`(`"access"` / `"refresh"`)・`exp` を詰める。検証側(`auth/dependencies.py` の `get_current_user`、`auth/service.py` の `refresh_token_verify`)は必ず `type` クレームを照合し、種別違いのトークンを拒否する — トークンを足す/変える時はこの `type` 規約を崩さないこと。`UserResponse`(`app/users/schemas.py`)は `password` を含まない(レスポンスから漏らさないための境界)。

### 認証フロー

全ルートは `app/main.py` で `prefix="/api"` の下にマウントされ、auth ルーターはさらに `prefix="/auth"` を持つ(下記の `/api/auth/...`)。users ルーターは追加 prefix なし(`/api/users`)。

1. `POST /api/auth/signup` — パスワードを `pwdlib`(argon2)でハッシュ化して保存。
2. `POST /api/auth/login` — `name` で検索しパスワード照合。成功で access(5分)+ refresh(10分)トークンを返す。
3. `GET /api/auth/me` — `OAuth2PasswordBearer` で Authorization ヘッダーから access トークンを取り、`get_current_user` が検証。
4. `POST /api/auth/token/refresh` — refresh トークンを検証し、両トークンを再発行。

トークン有効期限は `app/auth/router.py` 内に `timedelta` でハードコードされている(login と refresh の 2 箇所)。

### マイグレーション

`alembic/env.py` は `app.db.base` から `Base` を import し、その `base.py` が全モデルを import することで `target_metadata = Base.metadata` に全テーブルが登録される。**新しいモデルを追加したら `app/db/base.py` の import に足すこと**(足さないと autogenerate に拾われない)。接続先 URL は `alembic.ini` の `sqlalchemy.url`(`app/db/session.py` の `DATABASE_URL` とは別管理なので、変更時は両方を合わせる)。

## Notes

- `.env`(`secret` / `algorithm`)と `test.db` はローカル開発用。`secret`・`algorithm` は未設定だと `None` になり JWT 処理が失敗するため、起動前に `.env` が揃っていること。
- `login` はユーザー不在時に 404 を返す(ユーザー存在が漏れる)。コード内コメントの通り本番では 401 に寄せるのが望ましい、という既知の割り切り。
