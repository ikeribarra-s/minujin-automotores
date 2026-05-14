from sqlalchemy import String, Numeric, Text, Date, TIMESTAMP, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base
from backend.models.enums import EstadoCheque


class Cheque(Base):
    __tablename__ = "cheque"

    id: Mapped[int] = mapped_column(primary_key=True)
    cobro_id: Mapped[int] = mapped_column(ForeignKey("cobro.id"))
    numero: Mapped[str] = mapped_column(String(20))
    banco: Mapped[str] = mapped_column(String(80))
    titular: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_cobro: Mapped[date] = mapped_column(Date)
    estado: Mapped[EstadoCheque] = mapped_column(
        SAEnum(EstadoCheque, name="estado_cheque", create_type=False),
        default=EstadoCheque.pendiente,
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Scanner-populated fields
    monto_letras: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pagador_cuit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    beneficiario: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sucursal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    es_cpd: Mapped[bool] = mapped_column(Boolean, default=False)
    discrepancia_monto: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entrega: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
