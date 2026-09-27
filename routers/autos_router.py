from fastapi import APIRouter
from fastapi.params import Depends
from scipy.odr import Model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Autos, Models, AutoPhotos
from app.schemas import AutoResponse

router = APIRouter(prefix='/cars', tags=['Cars'])


@router.get('/', response_model=list[AutoResponse])
async def get_available_cars(db: AsyncSession = Depends(get_db)):
    stmt = select(Autos).options(selectinload(Autos.model).selectinload(Models.mark), selectinload(Autos.photos)).where(
        Autos.status == "Available")
    result = await db.execute(stmt)
    autos = result.scalars().all()
    return autos
