from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from app.auth import get_current_user
from app.database import get_db
from app.models import Autos, Models, Dealers, Clients, Deals, Marks
from app.schemas import AutoResponse, AutoCreate, DealerResponse, MarkResponse, ModelResponse, MarkCreate, ModelCreate, \
    DealResponse

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


@router.get('/marks', response_model=list[MarkResponse])
async def get_marks(db: AsyncSession = Depends(get_db), dealer: Dealers = Depends(require_dealer)):
    res = await db.execute(select(Marks))
    marks = res.scalars().all()
    return marks


@router.get('/models', response_model=list[ModelResponse] )
async def get_models(db: AsyncSession = Depends(get_db),dealer: Dealers = Depends(require_dealer)):
    res = await db.execute(select(Models))
    models = res.scalars().all()
    return models


@router.post('/add_mark', response_model=MarkResponse)
async def add_mark(mark: MarkCreate, db: AsyncSession = Depends(get_db), dealer: Dealers = Depends(require_dealer)):
    res = await db.execute(select(Marks).where(Marks.name_mark == mark.name_mark))
    mark_result = res.scalar_one_or_none()
    if mark_result is not None:
        raise HTTPException(status_code=409, detail='mark already exists')
    new_mark = Marks(name_mark=mark.name_mark)
    db.add(new_mark)
    await db.commit()
    await db.refresh(new_mark)
    return new_mark

@router.post('/add_model', response_model=ModelResponse)
async def add_model(model: ModelCreate, db: AsyncSession = Depends(get_db), dealer: Dealers = Depends(require_dealer)):
    res = await db.execute(select(Models).where(Models.name_model==model.name_model))
    model_res = res.scalar_one_or_none()
    if model_res is not None:
        raise HTTPException(status_code=409, detail='mark already exists')
    new_model = Models(id_mark=model.id_mark, name_model=model.name_model)
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)
    return new_model

@router.get('/{car_id}', response_model=AutoResponse)
async def get_car(car_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    stmt = select(Autos).options(selectinload(Autos.photos)).where(Autos.id_auto == car_id, Autos.status == "Available")
    res = await db.execute(stmt)
    car = res.scalar_one_or_none()
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


@router.post('/{car_id}/buy_car', response_model=DealResponse)
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
    deal = Deals(id_client=client.id_client, id_auto=auto.id_auto, deal_status='Processing',
                 date_deal=date.today(), sold_price=sold_price)
    auto.status = 'Reserved'
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal
