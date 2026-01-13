import crud
import models
from sqlalchemy import select
from typing import Optional
from fastapi import FastAPI
from dependancy import SessionDependency
from models import Session
from constants import SUCCESS_RESPONSE
from lifespan import lifespan
from schema import (
    CreateAdvertisementsResponse,
    UpdateAdvertisementsRequest,
    UpdateAdvertisementsResponse,
    GetAdvertisementsResponse,
    SearchAdvertisementsResponse,
    DeleteAdvertisementsResponse,
    CreateAdvertisementsRequest
)


app = FastAPI(
    title='Advertisements API',
    lifespan=lifespan
)


@app.post('/api/v1/advertisement', response_model=CreateAdvertisementsResponse)
async def create_advertisements(advertisement: CreateAdvertisementsRequest, session: SessionDependency):
    advertisement_dict = advertisement.model_dump(exclude_unset=True)
    advertisement_orm_obj = models.Advertisement(**advertisement_dict)
    await crud.add_item(session, advertisement_orm_obj)
    await session.refresh(advertisement_orm_obj)
    return {"id": advertisement_orm_obj.id}


@app.get('/api/v1/advertisement/{advertisement_id}', response_model=GetAdvertisementsResponse)
async def get_advertisements(advertisement_id: int, session: SessionDependency):
    advertisement_orm_obj = await crud.get_id_item(session, models.Advertisement, advertisement_id)
    return advertisement_orm_obj.id_dict


@app.get('/api/v1/advertisement/', response_model=SearchAdvertisementsResponse)
async def search_advertisements(
    session: SessionDependency,
    title: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    query = select(models.Advertisement)
    if title:
        query = query.where(models.Advertisement.title.contains(title))
    if author:
        query = query.where(models.Advertisement.author.contains(author))
    if min_price:
        query = query.where(models.Advertisement.price >= min_price)
    if max_price:
        query = query.where(models.Advertisement.price <= max_price)

    result = await session.execute(query)
    ads = result.scalars().all()
    return {"results": [ad.id_dict for ad in ads]}


@app.patch('/api/v1/advertisement/{advertisement_id}', response_model=UpdateAdvertisementsResponse)
async def update_advertisements(advertisement_id: int, advertisement_data: UpdateAdvertisementsRequest, session: SessionDependency):
    advertisement_dict = advertisement_data.model_dump(exclude_unset=True)
    advertisement_orm_obj = await crud.get_id_item(session, models.Advertisement, advertisement_id)
    for key, value in advertisement_dict.items():
        setattr(advertisement_orm_obj, key, value)
    await session.commit()
    await session.refresh(advertisement_orm_obj)
    return SUCCESS_RESPONSE


@app.delete('/api/v1/advertisement/{advertisement_id}', response_model=DeleteAdvertisementsResponse)
async def delete_advertisements(advertisement_id: int, session: SessionDependency):
    advertisement_orm_obj = await crud.get_id_item(session, models.Advertisement, advertisement_id)
    await crud.delete_item(session, advertisement_orm_obj)
    return SUCCESS_RESPONSE