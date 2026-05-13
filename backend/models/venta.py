from sqlalchemy import Numeric, Text, Date, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base
from backend.models.enums import FormaPagoVenta


class Venta(Base):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculo.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))
    precio_final: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    forma_pago: Mapped[FormaPagoVenta] = mapped_column(
        SAEnum(FormaPagoVenta, name="forma_pago_venta", create_type=False),
        default=FormaPagoVenta.contado,
    )
    fecha_venta: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
