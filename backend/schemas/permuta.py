from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class PermutaBase(BaseModel):
    venta_id: int
    vehiculo_recibido_id: int
    valor_tasacion: Decimal
    observaciones: Optional[str] = None


class PermutaCreate(PermutaBase):
    pass


class PermutaResponse(PermutaBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
