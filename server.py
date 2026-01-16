import crud
from auth import check_password, hash_password
from models import (
    ORM_OBJ,
    Advertisement,
    User,
    Token
)
from sqlalchemy import select
from typing import Optional
from fastapi import FastAPI, HTTPException
from dependancy import SessionDependency, TokenDependency, require_ownership
from models import Session
from constants import SUCCESS_RESPONSE
from lifespan import lifespan
from schema import (
    CreateAdvertisementsResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetUserResponse,
    LoginRequest,
    LoginResponse,
    UpdateAdvertisementsRequest,
    UpdateAdvertisementsResponse,
    GetAdvertisementsResponse,
    SearchAdvertisementsResponse,
    DeleteAdvertisementsResponse,
    CreateAdvertisementsRequest,
    UpdateUserRequest,
    UpdateUserResponse
)


app = FastAPI(
    title='Advertisements API',
    lifespan=lifespan
)




@app.post('/advertisement', response_model=CreateAdvertisementsResponse, status_code=201)
async def create_advertisements(
    advertisement: CreateAdvertisementsRequest,
    session: SessionDependency,
    token: TokenDependency
    ):
    advertisement_dict = advertisement.model_dump(exclude_unset=True)
    advertisement_orm_obj = Advertisement(**advertisement_dict, author_id = token.user_id)
    await crud.add_item(session, advertisement_orm_obj)
    return {"id": advertisement_orm_obj.id}


@app.get('/advertisement/{advertisement_id}', response_model=GetAdvertisementsResponse, status_code=200)
async def get_advertisements(advertisement_id: int, session: SessionDependency):
    advertisement_orm_obj = await crud.get_id_item(session, Advertisement, advertisement_id)
    return advertisement_orm_obj.id_dict



@app.get('/advertisement/', response_model=SearchAdvertisementsResponse)
async def search_advertisements(
    session: SessionDependency,
    title: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    offset: int = 0
):
    query = select(Advertisement).limit(limit).offset(offset)
    if title:
        query = query.where(Advertisement.title.ilike(f"%{title}%"))
    if author:
        query = query.join(Advertisement.user).where(User.login.ilike(f"%{author}%"))
    if min_price:
        query = query.where(Advertisement.price >= min_price)
    if max_price:
        query = query.where(Advertisement.price <= max_price)

    result = await session.execute(query)
    ads = result.scalars().unique().all()
    return {"results": [ad.id_dict for ad in ads]}


@app.patch('/advertisement/{advertisement_id}', response_model=UpdateAdvertisementsResponse, status_code=200)
async def update_advertisements(advertisement_id: int, advertisement_data: UpdateAdvertisementsRequest, session: SessionDependency, token: TokenDependency):
    advertisement_dict = advertisement_data.model_dump(exclude_unset=True)
    advertisement_orm_obj = await crud.get_id_item(session, Advertisement, advertisement_id)
    await require_ownership(token, advertisement_orm_obj)
    for key, value in advertisement_dict.items():
        setattr(advertisement_orm_obj, key, value)
    await session.commit()
    await session.refresh(advertisement_orm_obj)
    return SUCCESS_RESPONSE

@app.delete('/advertisement/{advertisement_id}', status_code=204)
async def delete_advertisements(advertisement_id: int, session: SessionDependency, token: TokenDependency):
    advertisement_orm_obj = await crud.get_id_item(session, Advertisement, advertisement_id)
    await require_ownership(token, advertisement_orm_obj)
    await crud.delete_item(session, advertisement_orm_obj)



@app.post('/login', tags=['login'], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    query = select(User).where(User.login == login_data.login)
    user = await session.scalar(query)
    if user is None or not check_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    token = Token(user_id=user.id)
    await crud.add_item(session, token)
    return {"token": token.token}


@app.post('/user', response_model=CreateUserResponse, status_code=201)
async def create_user(user: CreateUserRequest, session: SessionDependency):
    user_dict = user.model_dump(exclude_unset=True)
    user_dict["password"] = hash_password(user_dict["password"])
    user_orm_obj = User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return {"id": user_orm_obj.id}

@app.get('/user/{user_id}', response_model=GetUserResponse, status_code=200)
async def get_user(user_id: int, session: SessionDependency):
    user_orm_obj = await crud.get_id_item(session, User, user_id)
    return user_orm_obj.id_dict


@app.patch('/user/{user_id}', response_model=UpdateUserResponse, status_code=200)
async def update_user(user_id: int, user_data: UpdateUserRequest, session: SessionDependency, token: TokenDependency):
    user_dict = user_data.model_dump(exclude_unset=True)
    user_orm_obj = await crud.get_id_item(session, User, user_id)
    await require_ownership(token, user_orm_obj)
    for key, value in user_dict.items():
        setattr(user_orm_obj, key, value)
    await session.commit()
    await session.refresh(user_orm_obj)
    return SUCCESS_RESPONSE

@app.delete('/user/{user_id}', status_code=204)
async def user_delete(user_id: int, session: SessionDependency, token: TokenDependency):
    user_orm_obj = await crud.get_id_item(session, User, user_id)
    await require_ownership(token, user_orm_obj)
    await crud.delete_item(session, user_orm_obj)
