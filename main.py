from starlette.middleware.cors import CORSMiddleware

from app.models import *
from fastapi import FastAPI

from app.models import Base
from app.database import engine
import asyncio
from routers.autos_router import router as autos_router
from routers.auth_router import router as auth_router
from routers.dealer_roter import router as dealer_router
from routers.deals_router import router as deals_router
from routers.client_router import router as client_router
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()

app.include_router(autos_router)
app.include_router(auth_router)
app.include_router(dealer_router)
app.include_router(deals_router)
app.include_router(client_router)
app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:63342", "http://127.0.0.1:63342"],
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )
@app.get('/')
def root():
    return {"message": "api is running!"}


if __name__ == "__main__":
    asyncio.run(init_db())
