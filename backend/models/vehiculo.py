from sqlalchemy import String, SmallInteger, Integer, Numeric, Text, Date, TIMESTAMP, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base
from backend.models.enums import EstadoVehiculo, TipoVehiculo, Procedencia


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    marca: Mapped[str] = mapped_column(String(60))
    modelo: Mapped[str] = mapped_column(String(80))
    version: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    anio: Mapped[int] = mapped_column(SmallInteger)
    color: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    kilometraje: Mapped[int] = mapped_column(Integer, default=0)
    tipo: Mapped[TipoVehiculo] = mapped_column(
        SAEnum(TipoVehiculo, name="tipo_vehiculo", create_type=False),
        default=TipoVehiculo.usado,
    )
    numero_motor: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    numero_chasis: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    patente: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    precio_compra: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    precio_venta: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    estado: Mapped[EstadoVehiculo] = mapped_column(
        SAEnum(EstadoVehiculo, name="estado_vehiculo", create_type=False),
        default=EstadoVehiculo.disponible,
    )
    procedencia: Mapped[Procedencia] = mapped_column(
        SAEnum(Procedencia, name="procedencia", create_type=False),
        default=Procedencia.compra,
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    foto_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_ingreso: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
