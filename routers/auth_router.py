from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import hash_password, verify_password, create_access_token

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.exceptions import HTTPException

from app.database import get_db
from app.models import Clients, Dealers
from app.schemas import ClientResponse, ClientCreate, DealerResponse, DealerCreate

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register/client', response_model=ClientResponse)
async def register_client(user: ClientCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clients).where(Clients.phone_client == user.phone_client))
    existing_client = result.scalar_one_or_none()
    if existing_client:
        raise HTTPException(status_code=400, detail='client already exists')
    hashed_pass = hash_password(user.password)
    client = Clients(name_client=user.name_client, phone_client=user.phone_client, email=user.email,
                     address_client=user.address_client, password=hashed_pass)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.post('/register/dealer', response_model=DealerResponse)
async def register_dealer(user: DealerCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dealers).where(Dealers.phone_dealer == user.phone_dealer))
    existing_dealer = result.scalar_one_or_none()
    if existing_dealer:
        raise HTTPException(status_code=400, detail='dealer already exists')
    hashed_pass = hash_password(user.password)
    dealer = Dealers(name_dealer=user.name_dealer, phone_dealer=user.phone_dealer, address_dealer=user.address_dealer,
                     password=hashed_pass)
    db.add(dealer)
    await db.commit()
    await db.refresh(dealer)
    return dealer


@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    login_input = form_data.username
    password_input = form_data.password
    result = await db.execute(
        select(Dealers).where(Dealers.phone_dealer == login_input))
    dealer: Dealers = result.scalar_one_or_none()
    if dealer and verify_password(password_input, dealer.password):
        access_token = create_access_token({'sub': dealer.phone_dealer, 'role': 'dealer'})
        return {'access_token': access_token, 'token_type': "bearer"}

    result = await db.execute(
        select(Clients).where(Clients.phone_client == login_input))
    client: Clients = result.scalar_one_or_none()
    if client and verify_password(password_input, client.password):
        access_token = create_access_token({'sub': client.phone_client, 'role': 'client'})
        return {'access_token': access_token, 'token_type': "bearer"}
    raise HTTPException(status_code=401, detail='invalid login or password')
