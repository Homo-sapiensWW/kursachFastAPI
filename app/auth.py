import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Dealers, Clients

load_dotenv()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = "HS256"


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    try:
        decoded_jwt = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[ALGORITHM])
        phone: str = decoded_jwt.get('sub')
        role: str = decoded_jwt.get('role')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401)

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)

    if role == 'dealer':
        result = await db.execute(select(Dealers).where(Dealers.phone_dealer == phone))
        dealer = result.scalar_one_or_none()
        if dealer is None:
            raise HTTPException(status_code=401)
        return dealer
    elif role == 'client':
        result = await db.execute(select(Clients).where(Clients.phone_client == phone))
        client = result.scalar_one_or_none()
        if client is None:
            raise HTTPException(status_code=401)
        return client
    else:
        raise HTTPException(status_code=401)
