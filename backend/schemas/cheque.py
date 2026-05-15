from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Any, Optional
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
    # Scanner fields (optional — populated when cheque is created via scan)
    monto_letras: Optional[str] = None
    pagador_cuit: Optional[str] = None
    beneficiario: Optional[str] = None
    sucursal: Optional[str] = None
    localidad: Optional[str] = None
    es_cpd: bool = False
    discrepancia_monto: bool = False
    raw_ocr_text: Optional[str] = None
    raw_json: Optional[str] = None
    image_filename: Optional[str] = None
    entrega: Optional[str] = None


class ChequeCreate(ChequeBase):
    pass


class ChequeUpdate(BaseModel):
    numero: Optional[str] = None
    banco: Optional[str] = None
    titular: Optional[str] = None
    monto: Optional[Decimal] = None
    fecha_emision: Optional[date] = None
    fecha_cobro: Optional[date] = None
    estado: Optional[EstadoCheque] = None
    observaciones: Optional[str] = None
    entrega: Optional[str] = None
    monto_letras: Optional[str] = None
    pagador_cuit: Optional[str] = None
    beneficiario: Optional[str] = None
    sucursal: Optional[str] = None
    localidad: Optional[str] = None
    es_cpd: Optional[bool] = None
    discrepancia_monto: Optional[bool] = None


class ChequeResponse(ChequeBase):
    id: int
    estado: EstadoCheque
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ScanResult(BaseModel):
    """Returned by POST /cheques/scan — no DB write, user reviews before confirming."""
    tipo: Optional[str] = None
    banco: Optional[str] = None
    numero: Optional[str] = None
    monto_numerico: Optional[Decimal] = None
    monto_letras: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    pagador_nombre: Optional[str] = None
    pagador_cuit: Optional[str] = None
    beneficiario: Optional[str] = None
    sucursal: Optional[str] = None
    localidad: Optional[str] = None
    es_cpd: bool = False
    discrepancia_monto: bool = False
    raw_ocr_text: str = ""
    raw_json: Optional[Any] = None
    warning: Optional[str] = None
