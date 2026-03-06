from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine, BaseModel
from handlers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
