from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    xp: Mapped[int] = mapped_column(default=0)
    streak: Mapped[int] = mapped_column(default=0)
    hearts: Mapped[int] = mapped_column(default=5)