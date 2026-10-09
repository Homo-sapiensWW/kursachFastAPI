from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.auth import get_current_user
from app.database import get_db
from datetime import date
from app.models import Autos, Models, Dealers, Clients, Deals
from app.schemas import AutoResponse, AutoCreate, DealerResponse, DealResponse, PendingDealOut
from routers.autos_router import require_dealer
from sqlalchemy import func
import decimal
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/dealer', tags=['dealer'], dependencies=[Depends(require_dealer)])


@router.patch('/{deal_id}/confirm', response_model=DealResponse)
async def confirm_deal(deal_id: int, db: AsyncSession = Depends(get_db), dealer: Dealers = Depends(require_dealer)):
    result = await db.execute(select(Deals).options(selectinload(Deals.auto), selectinload(Deals.client)).where(Deals.id_deal == deal_id))
    deal: Deals = result.scalar_one_or_none()
    if deal is None:
        raise HTTPException(status_code=404, detail='deal not found')
    if deal.deal_status != 'Processing':
        raise HTTPException(status_code=409, detail='deal already processed')
    deal.deal_status = 'Confirmed'
    deal.date_sale = date.today()
    deal.id_dealer = dealer.id_dealer

    auto = deal.auto
    auto.status = "Sold"
    client = deal.client
    count_deals = await db.scalar(
        select(func.count(Deals.id_deal)).where(Deals.id_client == client.id_client, Deals.deal_status == 'Confirmed'))
    current_discount = await db.scalar(select(Clients.discount).where(Clients.id_client == client.id_client))
    if count_deals >= 2 and current_discount == 0:
        client.discount = decimal.Decimal('7')
    await db.commit()
    return deal


@router.patch('/{deal_id}/reject', response_model=DealResponse)
async def reject_deal(deal_id: int, dealer: Dealers = Depends(require_dealer), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deals).options(selectinload(Deals.auto)).where(Deals.id_deal == deal_id))
    deal: Deals = result.scalar_one_or_none()
    if deal is None:
        raise HTTPException(status_code=404, detail='deal not found')
    if deal.deal_status != 'Processing':
        raise HTTPException(status_code=409, detail='deal already processed')
    deal_data = DealResponse.model_validate(deal)
    await db.delete(deal)
    auto = deal.auto
    auto.status = "Available"
    await db.commit()
    return deal_data


@router.get('/pending', response_model=list[PendingDealOut])
async def get_pending_deals(dealer: Dealers = Depends(require_dealer), db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Deals)
        .options(
            selectinload(Deals.client),
            selectinload(Deals.auto).selectinload(Autos.model).selectinload(Models.mark),
        )
        .where(Deals.deal_status == 'Processing')
    )
    result = await db.execute(stmt)
    deals = result.scalars().all()

    return [
        PendingDealOut(
            id_deal=d.id_deal,
            date_deal=d.date_deal,
            sold_price=d.sold_price,
            client_name=d.client.name_client,
            client_phone=d.client.phone_client,
            client_email=d.client.email,
            mark_name=d.auto.model.mark.name_mark,
            model_name=d.auto.model.name_model,
            year_release=d.auto.year_release,
            mileage=d.auto.mileage,
            engine_type=d.auto.engine_type,
            engine_capacity=d.auto.engine_capacity,
        )
        for d in deals
    ]
