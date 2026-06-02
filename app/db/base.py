# Alembic の autogenerate がモデルを取りこぼさないための集約ファイル。
# Base.metadata に全テーブルを登録するため、ここで Base と全モデルを import する。
# 新しいモデルを追加したら、ここに import を足すこと。
from app.db.base_class import Base  # noqa: F401
from app.models import User  # noqa: F401
