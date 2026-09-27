from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Marks(Base):
    __tablename__ = 'marks'

    mark_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_mark: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    models: Mapped[list["Models"]] = relationship(back_populates="mark")


class Models(Base):
    __tablename__ = "models"

    id_model: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mark: Mapped[int] = mapped_column(
        ForeignKey("marks.mark_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    name_model: Mapped[str] = mapped_column(String(100), nullable=False)

    mark: Mapped["Marks"] = relationship(back_populates="models")
    autos: Mapped[list["Autos"]] = relationship(back_populates="model")


class Dealers(Base):
    __tablename__ = "dealers"

    id_dealer: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_dealer: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_dealer: Mapped[str] = mapped_column(String(20), nullable=False)
    address_dealer: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    deals: Mapped[list["Deals"]] = relationship(back_populates="dealer")


class Clients(Base):
    __tablename__ = "clients"

    id_client: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_client: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_client: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(150))
    address_client: Mapped[str | None] = mapped_column(String(255))
    # ПРИМЕЧАНИЕ: DEFAULT 0, CHECK IN (0, 7) — перенёс как есть из исходной схемы.
    discount: Mapped[Decimal] = mapped_column(default=0)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    deals: Mapped[list["Deals"]] = relationship(back_populates="client")

    __table_args__ = (
        CheckConstraint("discount IN (0, 7)", name="ck_client_discount_values"),
        # ПРИМЕЧАНИЕ: GLOB — синтаксис SQLite, в Postgres его нет.
        # Заменил на regex-оператор Postgres (~). Не проверял на реальных номерах — протестируй.
        CheckConstraint(
            r"phone_client ~ '^\+380[0-9]{9}$'",
            name="ck_client_phone_format",
        ),
    )


class Autos(Base):
    __tablename__ = "autos"

    id_auto: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_model: Mapped[int] = mapped_column(
        ForeignKey("models.id_model", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    vin: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(nullable=False)
    year_release: Mapped[int] = mapped_column(nullable=False)
    mileage: Mapped[int] = mapped_column(nullable=False)
    date_to_sale: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Available")

    engine_type: Mapped[str] = mapped_column(String(20), nullable=False)
    engine_capacity: Mapped[Decimal] = mapped_column(nullable=False)
    transmission: Mapped[str] = mapped_column(String(20), nullable=False)
    drive_type: Mapped[str] = mapped_column(String(10), nullable=False, default="FWD")
    color: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)

    model: Mapped["Models"] = relationship(back_populates="autos")
    photos: Mapped[list["AutoPhotos"]] = relationship(
        back_populates="auto", cascade="all, delete-orphan"
    )
    deals: Mapped[list["Deals"]] = relationship(back_populates="auto")

    __table_args__ = (
        CheckConstraint("length(vin) = 17", name="ck_auto_vin_len"),
        CheckConstraint("price > 0", name="ck_auto_price_positive"),
        CheckConstraint(
            "year_release >= 1900 AND year_release <= 2025", name="ck_auto_year_range"
        ),
        CheckConstraint("mileage >= 0", name="ck_auto_mileage_nonneg"),
        CheckConstraint(
            "status IN ('Available', 'Reserved', 'Sold')", name="ck_auto_status_values"
        ),
        CheckConstraint(
            "engine_type IN ('Petrol', 'Diesel', 'Electric', 'Hybrid')",
            name="ck_auto_engine_type_values",
        ),
        CheckConstraint(
            "engine_capacity > 0 AND engine_capacity <= 10.0",
            name="ck_auto_engine_capacity_range",
        ),
        CheckConstraint(
            "transmission IN ('Manual', 'Automatic', 'Robot', 'CVT')",
            name="ck_auto_transmission_values",
        ),
        CheckConstraint(
            "drive_type IN ('FWD', 'RWD', 'AWD')", name="ck_auto_drive_type_values"
        ),
    )


class AutoPhotos(Base):
    __tablename__ = "autos_photos"

    id_photo: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_auto: Mapped[int] = mapped_column(
        ForeignKey("autos.id_auto", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    photo_path: Mapped[str] = mapped_column(String(500), nullable=False)

    auto: Mapped["Autos"] = relationship(back_populates="photos")


class Deals(Base):
    __tablename__ = "deals"

    id_deal: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_client: Mapped[int] = mapped_column(
        ForeignKey("clients.id_client", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    id_auto: Mapped[int] = mapped_column(
        ForeignKey("autos.id_auto", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    id_dealer: Mapped[int | None] = mapped_column(
        ForeignKey("dealers.id_dealer", onupdate="CASCADE", ondelete="RESTRICT")
    )

    deal_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Processing"
    )
    date_deal: Mapped[date] = mapped_column(nullable=False)
    date_sale: Mapped[date | None] = mapped_column()
    sold_price: Mapped[Decimal] = mapped_column(nullable=False)

    client: Mapped["Clients"] = relationship(back_populates="deals")
    auto: Mapped["Autos"] = relationship(back_populates="deals")
    dealer: Mapped["Dealers | None"] = relationship(back_populates="deals")

    __table_args__ = (
        CheckConstraint(
            "deal_status IN ('Processing', 'Confirmed')", name="ck_deal_status_values"
        ),
        CheckConstraint("sold_price > 0", name="ck_deal_sold_price_positive"),
    )
