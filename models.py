import datetime
from uuid import UUID
from sqlalchemy import (
    Float,
    Integer,
    String,
    DateTime,
    func,
    ForeignKey,
    UUID
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
)

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine
    )

from config import PG_DSN
from typing import List
from custom_types import ROLE



engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
        )
    login: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
        )
    password: Mapped[str] = mapped_column(
        String,
        nullable=False
        )
    tokens: Mapped[List["Token"]] = relationship(
        "Token",
        back_populates="user",
        cascade="all, " \
        "delete-orphan",
        lazy="joined"
        )
    role: Mapped[ROLE] = mapped_column(String, default='user')
    advertisements = relationship("Advertisement", back_populates="user", primaryjoin="User.id==Advertisement.author_id")
    @property
    def id_dict(self):
        return {
            'id': self.id,
            'login': self.login
            }

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
        )
    token: Mapped[UUID] = mapped_column(
        UUID,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True
        )
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now()
        )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tokens",
        lazy="joined"
        )
    @property
    def id_dict(self):
        return {
            'token': self.token
            }


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
        )
    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
        )
    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
        )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
        )
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
        )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="advertisements",
        lazy="joined"
        )
    @property
    def id_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'created': self.created.isoformat() if self.created else None,
            'author_id': self.author_id,
            'author': self.user.login if self.user else None
        }
ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()