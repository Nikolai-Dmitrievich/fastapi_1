import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SuccessResponse(BaseModel):
    status: Literal["success"]


class IdResponse(BaseModel):
    id: int


class CreateAdvertisementsRequest(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)


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
    author: Optional[str] = None
    created: datetime.datetime


class SearchAdvertisementsResponse(BaseModel):
    results: list[GetAdvertisementsResponse]


class DeleteAdvertisementsResponse(SuccessResponse):
    pass

class BaseUserRequest(BaseModel):
    login: str
    password: str

    @field_validator('password')
    @classmethod
    def secure_password(cls, v: str | None):
        if v and len(v) < 8:
            raise ValueError('Пароль не может быть меньше 8 символов')
        return v


class CreateUserRequest(BaseUserRequest):
    pass


class LoginRequest(BaseUserRequest):
    pass


class LoginResponse(BaseModel):
    token: UUID


class CreateUserResponse(IdResponse):
    pass

class GetUserResponse(BaseModel):
    id: int
    login: str

class UpdateUserRequest(BaseModel):
    login: str | None = None
    password: str | None = None

class UpdateUserResponse(SuccessResponse):
    pass

class DeleteUserResponse(SuccessResponse):
    pass