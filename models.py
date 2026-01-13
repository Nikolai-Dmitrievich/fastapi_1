import datetime
from sqlalchemy import (
    Float,
    Integer,
    String,
    DateTime,
    func
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped
)

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine
    )

from config import PG_DSN


engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

class Base(DeclarativeBase, AsyncAttrs):
    pass

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
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    @property
    def id_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'created': self.created.isoformat() if self.created else None,
            'author': self.author
        }
ORM_OBJ = Advertisement
ORM_CLS = type[Advertisement]


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()