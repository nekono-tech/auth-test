from app.db.base_class import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base, TimestampMixin):
    __tablename__ = "auth_user"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )
    password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
