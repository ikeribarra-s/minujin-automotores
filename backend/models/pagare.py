from sqlalchemy import String, Numeric, Text, Date, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base
from backend.models.enums import EstadoPagare


class Pagare(Base):
    __tablename__ = "pagare"

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venta.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(20))
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    vencimiento: Mapped[date] = mapped_column(Date)
    firmante: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    calle: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estado: Mapped[EstadoPagare] = mapped_column(
        SAEnum(EstadoPagare, name="estado_pagare", create_type=False),
        default=EstadoPagare.pendiente,
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
