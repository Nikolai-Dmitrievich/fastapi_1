import datetime
from typing import Literal
from pydantic import BaseModel, Field
from typing import Optional


class SuccessResponse(BaseModel):
    status: Literal["success"]


class IdResponse(BaseModel):
    id: int


class CreateAdvertisementsRequest(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)
    author: str


class CreateAdvertisementsResponse(IdResponse):
    pass


class UpdateAdvertisementsRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Optional[float] = Field(None, gt=0)

class UpdateAdvertisementsResponse(SuccessResponse):
    pass


class GetAdvertisementsResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author: str
    created: datetime.datetime


class SearchAdvertisementsResponse(BaseModel):
    results: list[GetAdvertisementsResponse]


class DeleteAdvertisementsResponse(SuccessResponse):
    pass