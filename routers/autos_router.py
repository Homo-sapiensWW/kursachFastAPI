import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from app.auth import get_current_user
from app.database import get_db
from app.models import Autos, Models, Dealers, Clients, Deals
from app.schemas import AutoResponse, AutoCreate, DealerResponse

router = APIRouter(prefix='/cars', tags=['Cars'])


def require_dealer(dealer=Depends(get_current_user)):
    if not isinstance(dealer, Dealers):
        raise HTTPException(status_code=403, detail='only for dealers')
    return dealer


def require_client(client=Depends(get_current_user)):
    if not isinstance(client, Clients):
        raise HTTPException(status_code=403, detail='only for clients')
    return client


@router.get('', response_model=list[AutoResponse])
async def get_available_cars(db: AsyncSession = Depends(get_db)):
    stmt = select(Autos).options(selectinload(Autos.model).selectinload(Models.mark), selectinload(Autos.photos)).where(
        Autos.status == "Available")
    result = await db.execute(stmt)
    autos = result.scalars().all()
    return autos

@router.get('/{car_id}', response_model=AutoResponse)
async def get_car(car_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Autos).where(Autos.id_auto==car_id, Autos.status=="Available"))
    car = result.scalar_one_or_none()
    if car is None:
        raise HTTPException(status_code=404, detail='car not found')
    return car

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


@router.post('/{car_id}/buy_car', response_model=DealerResponse)
async def by_car(car_id: int, client: Clients = Depends(require_client),
                 db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Autos).where(Autos.id_auto == car_id))
    auto: Autos = result.scalar_one_or_none()
    if auto is None:
        raise HTTPException(status_code=404, detail='auto not found')
    if auto.status != "Available":
        raise HTTPException(status_code=409, detail='auto already reserved')
    discount = client.discount
    sold_price = auto.price * (1 - discount / 100)
    deal = Deals(id_client=client.id_client, id_auto=auto.id_auto, id_dealer=None, deal_status='Processing',
                 date_deal=date.today(), sold_price=sold_price)
    auto.status = 'Reserved'
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal
