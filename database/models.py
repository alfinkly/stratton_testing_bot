from datetime import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at_pk = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at_pk = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                  onupdate=text("TIMEZONE('utc', now())"))]


class Base(DeclarativeBase):
    __table_args__ = {'extend_existing': True}


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    user_id: Mapped[int]
    username: Mapped[str]
    fullname: Mapped[str]
    test_status: Mapped[int]
    phone_number: Mapped[str]
    task: Mapped[str] = mapped_column(nullable=True)
    testing_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[created_at_pk]
    updated_at: Mapped[updated_at_pk]

# TODO Добавить для тестирования таблицу