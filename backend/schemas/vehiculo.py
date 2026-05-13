import re
from pydantic import BaseModel, ConfigDict, field_validator
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import EstadoVehiculo, TipoVehiculo, Procedencia

_MERCOSUR = re.compile(r'^[A-Z]{2}\d{3}[A-Z]{2}$')
_ANTIGUO = re.compile(r'^[A-Z]{3}\d{3}$')


def _normalizar_patente(v: str) -> str:
    """Valida y normaliza patente argentina. Acepta con o sin espacios."""
    s = v.upper().replace(" ", "")
    if _MERCOSUR.match(s):
        return f"{s[:2]} {s[2:5]} {s[5:]}"   # AB 123 CD
    if _ANTIGUO.match(s):
        return f"{s[:3]} {s[3:]}"             # ABC 123
    raise ValueError("Formato inválido. Usar: AB 123 CD o ABC 123")


class VehiculoBase(BaseModel):
    marca: str
    modelo: str
    version: Optional[str] = None
    anio: int
    color: Optional[str] = None
    kilometraje: int = 0
    tipo: TipoVehiculo = TipoVehiculo.usado
    numero_motor: Optional[str] = None
    numero_chasis: Optional[str] = None
    patente: Optional[str] = None
    precio_compra: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    estado: EstadoVehiculo = EstadoVehiculo.disponible
    procedencia: Procedencia = Procedencia.compra
    observaciones: Optional[str] = None

    @field_validator("patente", mode="before")
    @classmethod
    def validar_patente(cls, v):
        if v is None or v == "":
            return None
        return _normalizar_patente(v)


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    version: Optional[str] = None
    anio: Optional[int] = None
    color: Optional[str] = None
    kilometraje: Optional[int] = None
    tipo: Optional[TipoVehiculo] = None
    numero_motor: Optional[str] = None
    numero_chasis: Optional[str] = None
    patente: Optional[str] = None
    precio_compra: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    estado: Optional[EstadoVehiculo] = None
    procedencia: Optional[Procedencia] = None
    observaciones: Optional[str] = None

    @field_validator("patente", mode="before")
    @classmethod
    def validar_patente(cls, v):
        if v is None or v == "":
            return None
        return _normalizar_patente(v)


class VehiculoResponse(VehiculoBase):
    id: int
    foto_url: Optional[str] = None
    fecha_ingreso: date
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
