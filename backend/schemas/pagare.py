from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import EstadoPagare


class PagareBase(BaseModel):
    venta_id: Optional[int] = None
    numero: str
    monto: Decimal
    vencimiento: date
    firmante: Optional[str] = None
    calle: Optional[str] = None
    localidad: Optional[str] = None
    observaciones: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    image_filename: Optional[str] = None


class PagareCreate(PagareBase):
    pass


class PagareUpdate(BaseModel):
    venta_id: Optional[int] = None
    numero: Optional[str] = None
    monto: Optional[Decimal] = None
    vencimiento: Optional[date] = None
    firmante: Optional[str] = None
    calle: Optional[str] = None
    localidad: Optional[str] = None
    estado: Optional[EstadoPagare] = None
    observaciones: Optional[str] = None


class PagareResponse(PagareBase):
    id: int
    estado: EstadoPagare
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
