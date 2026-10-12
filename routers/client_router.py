from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from datetime import date
from app.models import Autos, Models, Dealers, Clients, Deals
from app.schemas import DealResponse, PendingDealOut, ClientResponse, ProfileOut, ClientStatistic, ClientHistory
from routers.autos_router import require_dealer, require_client
from sqlalchemy import func
import decimal
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/client', tags=['/Client'], dependencies=[Depends(require_client)])


@router.get('/about_me', response_model=ProfileOut)
async def info_about_me(client: Clients = Depends(require_client), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Deals).options(selectinload(Deals.auto).selectinload(Autos.model).selectinload(Models.mark),
                              selectinload(Deals.auto).selectinload(Autos.photos)).where(
            Deals.id_client == client.id_client).order_by(Deals.date_deal.desc()))
    deals: list[Deals] = res.scalars().all()

    count_confirmed_deals = await db.scalar(
        select(func.count(Deals.id_deal)).where(Deals.id_client == client.id_client, Deals.deal_status == "Confirmed"))
    count_deals = await db.scalar(
        select(func.count(Deals.id_deal)).where(Deals.id_client == client.id_client))
    sum_deals_for_client = await db.scalar(
        select(func.coalesce(func.sum(Deals.sold_price), 0)).where(Deals.id_client == client.id_client,
                                                                   Deals.deal_status == 'Confirmed'))
    history = []
    for d in deals:
        photos = d.auto.photos
        if photos:
            first_photo = d.auto.photos[0].photo_path
        else:
            first_photo = None
        client_history = ClientHistory(status=d.deal_status, date_deal=d.date_deal, price=d.sold_price, mark=d.auto.model.mark.name_mark, model=d.auto.model.name_model, year_release=d.auto.year_release, photo_path=first_photo)
        history.append(client_history)
    return ProfileOut(client=ClientResponse.model_validate(client),
                      stats=ClientStatistic(total_deals=count_deals, confirmed_deals=count_confirmed_deals,
                                            sum_confirmed_deals=sum_deals_for_client),
                      history=history)
