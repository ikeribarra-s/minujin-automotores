from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import FormaPagoVenta


class VentaBase(BaseModel):
    vehiculo_id: int
    cliente_id: int
    precio_final: Decimal
    forma_pago: FormaPagoVenta = FormaPagoVenta.contado
    observaciones: Optional[str] = None


class VentaCreate(VentaBase):
    pass


class VentaUpdate(BaseModel):
    precio_final: Optional[Decimal] = None
    forma_pago: Optional[FormaPagoVenta] = None
    observaciones: Optional[str] = None


class VentaResponse(VentaBase):
    id: int
    fecha_venta: date
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VentaLabel(BaseModel):
    id: int
    label: str
