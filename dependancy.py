from sqlalchemy.ext.asyncio import AsyncSession
from models import Session
from fastapi import Depends
from typing import Annotated


async def get_session():
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]