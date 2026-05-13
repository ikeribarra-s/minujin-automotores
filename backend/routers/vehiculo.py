from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from backend.database import get_db
from backend.auth import verify_token
from backend.models.vehiculo import Vehiculo
from backend.models.enums import EstadoVehiculo
from backend.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


@router.get("/", response_model=List[VehiculoResponse])
async def list_vehiculos(
    estado: Optional[EstadoVehiculo] = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = select(Vehiculo)
    if estado:
        q = q.where(Vehiculo.estado == estado)
    result = await db.execute(q.order_by(Vehiculo.fecha_ingreso.desc()))
    return result.scalars().all()


@router.get("/{id}", response_model=VehiculoResponse)
async def get_vehiculo(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    v = await db.get(Vehiculo, id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return v


@router.post("/", response_model=VehiculoResponse, status_code=201)
async def create_vehiculo(
    data: VehiculoCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    v = Vehiculo(**data.model_dump())
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


@router.put("/{id}", response_model=VehiculoResponse)
async def update_vehiculo(
    id: int,
    data: VehiculoUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    v = await db.get(Vehiculo, id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(v, field, val)
    await db.commit()
    await db.refresh(v)
    return v


@router.delete("/{id}", status_code=204)
async def delete_vehiculo(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    v = await db.get(Vehiculo, id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if v.estado in (EstadoVehiculo.vendido, EstadoVehiculo.reservado):
        raise HTTPException(status_code=409, detail="No se puede eliminar un vehículo vendido o reservado")
    await db.delete(v)
    await db.commit()
