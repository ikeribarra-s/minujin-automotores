from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from backend.models.enums import EstadoVehiculo, TipoVehiculo, Procedencia


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


class VehiculoResponse(VehiculoBase):
    id: int
    fecha_ingreso: date
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
