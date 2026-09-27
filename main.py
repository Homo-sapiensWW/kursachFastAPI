from app.models import *
from fastapi import FastAPI

from app.models import Base
from app.database import engine
import asyncio
from routers.autos_router import router as autos_router

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()

app.include_router(autos_router)
@app.get('/')
def root():
    return {"message": "api is running!"}


if __name__ == "__main__":
    asyncio.run(init_db())
