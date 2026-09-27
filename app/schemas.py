"""
Тот же набор схем, но БЕЗ Base-классов — просто Create/Response напрямую,
как ты обычно делал. Поля, которые есть и там и там, дублируются —
это и есть цена отказа от Base (см. предыдущий файл schemas.py для сравнения).
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field



class MarkCreate(BaseModel):
    name_mark: str = Field(max_length=50)


class MarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mark: int
    name_mark: str = Field(max_length=50)



class ModelCreate(BaseModel):
    id_mark: int
    name_model: str = Field(max_length=100)


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_model: int
    id_mark: int
    name_model: str = Field(max_length=100)



class DealerCreate(BaseModel):
    name_dealer: str = Field(max_length=150)
    phone_dealer: str = Field(max_length=20)
    address_dealer: str | None = None
    password: str = Field(min_length=6)


class DealerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_dealer: int
    name_dealer: str = Field(max_length=150)
    phone_dealer: str = Field(max_length=20)
    address_dealer: str | None = None




class ClientCreate(BaseModel):
    name_client: str = Field(max_length=150)
    phone_client: str = Field(pattern=r"^\+380\d{9}$")
    email: str | None = None
    address_client: str | None = None
    password: str = Field(min_length=6)


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_client: int
    name_client: str = Field(max_length=150)
    phone_client: str = Field(pattern=r"^\+380\d{9}$")
    email: str | None = None
    address_client: str | None = None
    discount: Decimal



class AutoCreate(BaseModel):
    id_model: int
    vin: str = Field(min_length=17, max_length=17)
    price: Decimal = Field(gt=0)
    year_release: int = Field(ge=1900, le=2025)
    mileage: int = Field(ge=0)
    date_to_sale: date
    engine_type: Literal["Petrol", "Diesel", "Electric", "Hybrid"]
    engine_capacity: Decimal = Field(gt=0, le=10)
    transmission: Literal["Manual", "Automatic", "Robot", "CVT"]
    drive_type: Literal["FWD", "RWD", "AWD"] = "FWD"
    color: str | None = None
    description: str | None = None


class AutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_auto: int
    id_model: int
    vin: str = Field(min_length=17, max_length=17)
    price: Decimal = Field(gt=0)
    year_release: int = Field(ge=1900, le=2025)
    mileage: int = Field(ge=0)
    date_to_sale: date
    status: Literal["Available", "Reserved", "Sold"]
    engine_type: Literal["Petrol", "Diesel", "Electric", "Hybrid"]
    engine_capacity: Decimal = Field(gt=0, le=10)
    transmission: Literal["Manual", "Automatic", "Robot", "CVT"]
    drive_type: Literal["FWD", "RWD", "AWD"]
    color: str | None = None
    description: str | None = None
    photos: list["AutoPhotoResponse"] = []



class AutoPhotoCreate(BaseModel):
    id_auto: int
    photo_path: str = Field(max_length=500)


class AutoPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_photo: int
    photo_path: str = Field(max_length=500)



class DealCreate(BaseModel):
    id_client: int
    id_auto: int
    id_dealer: int | None = None
    sold_price: Decimal = Field(gt=0)


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_deal: int
    id_client: int
    id_auto: int
    id_dealer: int | None = None
    sold_price: Decimal = Field(gt=0)
    deal_status: Literal["Processing", "Confirmed"]
    date_deal: date
    date_sale: date | None = None


AutoResponse.model_rebuild()