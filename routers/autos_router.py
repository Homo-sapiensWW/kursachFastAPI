from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import Autos, Models, Dealers
from app.schemas import AutoResponse, AutoCreate

router = APIRouter(prefix='/cars', tags=['Cars'])


def require_dealer(dealer=Depends(get_current_user)):
    if not isinstance(dealer, Dealers):
        raise HTTPException(status_code=403, detail='only for dealers')
    return dealer


@router.get('/', response_model=list[AutoResponse])
async def get_available_cars(db: AsyncSession = Depends(get_db)):
    stmt = select(Autos).options(selectinload(Autos.model).selectinload(Models.mark), selectinload(Autos.photos)).where(
        Autos.status == "Available")
    result = await db.execute(stmt)
    autos = result.scalars().all()
    return autos


@router.post('/add_car', response_model=AutoCreate)
async def add_car(auto: AutoCreate, db: AsyncSession = Depends(get_db), dealer: Dealers = Depends(require_dealer)):
    auto = Autos(id_model=auto.id_model, vin=auto.vin, price=auto.price, year_release=auto.year_release,
                 mileage=auto.mileage, date_to_sale=auto.date_to_sale,
                 engine_type=auto.engine_type, engine_capacity=auto.engine_capacity, transmission=auto.transmission,
                 drive_type=auto.drive_type,
                 color=auto.color, description=auto.description)
    db.add(auto)
    await db.commit()
    await db.refresh(auto)
    return auto
