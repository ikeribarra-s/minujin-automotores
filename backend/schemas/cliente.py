from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class ClienteResponse(ClienteBase):
    id: int
    fecha_alta: date
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
