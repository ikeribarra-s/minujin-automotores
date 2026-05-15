from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import ConceptoCobro, FormaPagoCobro


class CobroBase(BaseModel):
    venta_id: int
    cliente_id: int
    concepto: ConceptoCobro = ConceptoCobro.saldo
    monto: Decimal
    forma_pago: FormaPagoCobro = FormaPagoCobro.efectivo
    observaciones: Optional[str] = None


class CobroCreate(CobroBase):
    pass


class CobroUpdate(BaseModel):
    monto: Optional[Decimal] = None
    concepto: Optional[ConceptoCobro] = None
    forma_pago: Optional[FormaPagoCobro] = None
    observaciones: Optional[str] = None


class CobroResponse(CobroBase):
    id: int
    fecha: date
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
