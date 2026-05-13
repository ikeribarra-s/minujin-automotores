from sqlalchemy import Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base


class Permuta(Base):
    __tablename__ = "permuta"

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id"))
    vehiculo_recibido_id: Mapped[int] = mapped_column(ForeignKey("vehiculo.id"))
    valor_tasacion: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
