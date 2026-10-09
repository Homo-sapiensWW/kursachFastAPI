from dotenv.variables import Literal
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.auth import get_current_user
from app.database import get_db
from datetime import date
from typing import Literal
from app.models import Autos, Models, Dealers, Clients, Deals
from app.schemas import AutoResponse, AutoCreate, DealerResponse, DealResponse, PendingDealOut, AllDealsOut
from routers.autos_router import require_dealer
from sqlalchemy import func
import decimal
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/deals', tags=['/Deals'], dependencies=[Depends(require_dealer)])


@router.get('/all_deals', response_model=list[AllDealsOut])
async def get_all_deals(status: Literal["Processing", "Confirmed"] | None = None, dealer_id: int | None = None,
                        date_from: date | None = None,
                        date_to: date | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Deals).options(selectinload(Deals.client),
                                 selectinload(Deals.auto).selectinload(Autos.model).selectinload(Models.mark),
                                 selectinload(Deals.dealer))
    if status is not None:
        stmt = stmt.where(Deals.deal_status == status)
    if dealer_id is not None:
        stmt = stmt.where(Deals.id_dealer == dealer_id)
    if date_from is not None:
        stmt = stmt.where(Deals.date_deal >= date_from)
    if date_to is not None:
        stmt = stmt.where(Deals.date_deal <= date_to)

    stmt = stmt.order_by(Deals.date_deal.desc())
    res = await db.execute(stmt)
    deals = res.scalars().all()
    return [
        AllDealsOut(id_deal=d.id_deal, date_deal=d.date_deal, sold_price=d.sold_price, client_name=d.client.name_client,
                    client_phone=d.client.phone_client, client_email=d.client.email,
                    mark_name=d.auto.model.mark.name_mark, model_name=d.auto.model.name_model,
                    year_release=d.auto.year_release, dealer_name=d.dealer.name_dealer if d.dealer else None,
                    date_sale=d.date_sale, deal_status=d.deal_status) for d in deals]
