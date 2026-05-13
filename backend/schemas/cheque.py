from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import EstadoCheque


class ChequeBase(BaseModel):
    cobro_id: int
    numero: str
    banco: str
    titular: Optional[str] = None
    monto: Decimal
    fecha_emision: Optional[date] = None
    fecha_cobro: date
    observaciones: Optional[str] = None


class ChequeCreate(ChequeBase):
    pass


class ChequeUpdate(BaseModel):
    estado: Optional[EstadoCheque] = None
    observaciones: Optional[str] = None


class ChequeResponse(ChequeBase):
    id: int
    estado: EstadoCheque
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
