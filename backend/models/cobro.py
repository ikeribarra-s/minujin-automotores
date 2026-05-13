from sqlalchemy import Numeric, Text, Date, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from backend.database import Base
from backend.models.enums import ConceptoCobro, FormaPagoCobro


class Cobro(Base):
    __tablename__ = "cobro"

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))
    concepto: Mapped[ConceptoCobro] = mapped_column(
        SAEnum(ConceptoCobro, name="concepto_cobro", create_type=False),
        default=ConceptoCobro.saldo,
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    forma_pago: Mapped[FormaPagoCobro] = mapped_column(
        SAEnum(FormaPagoCobro, name="forma_pago_cobro", create_type=False),
        default=FormaPagoCobro.efectivo,
    )
    fecha: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
