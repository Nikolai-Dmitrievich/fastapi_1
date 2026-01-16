from sqlalchemy.ext.asyncio import AsyncSession
from models import ORM_OBJ, Session
from fastapi import Depends, HTTPException, Header
from typing import Annotated
from uuid import UUID
from sqlalchemy import select
from models import Token
from datetime import datetime, timedelta
from constants import TOKEN_TTL_SEC




async def get_session():
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]

async def get_token(
        x_token: Annotated[UUID, Header()], session: SessionDependency
) -> Token:
    query = select(Token).where(
        Token.token == x_token,
        Token.creation_time
        >= (datetime.now() - timedelta(seconds=TOKEN_TTL_SEC))
    )
    token = await session.scalar(query)
    if token is None:
        raise HTTPException(status_code=401, detail='Token not found')
    return token
TokenDependency = Annotated[Token, Depends(get_token)]

async def require_ownership(token: TokenDependency, obj: ORM_OBJ):
    if token.user.role == "admin" or token.user_id == getattr(obj, 'author_id', obj.id):
        return obj
    raise HTTPException(403, 'Insufficient privileges')