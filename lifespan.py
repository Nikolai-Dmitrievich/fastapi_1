
from fastapi import FastAPI
from models import close_orm, init_orm
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("START")
    await init_orm()

    yield
    await close_orm()
    print("FINISH")