from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.database import get_db
from backend.auth import verify_token
from backend.models.venta import Venta
from backend.models.vehiculo import Vehiculo
from backend.models.cliente import Cliente
from backend.models.enums import EstadoVehiculo
from backend.schemas.venta import VentaCreate, VentaUpdate, VentaResponse, VentaLabel

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/labels", response_model=List[VentaLabel])
async def list_venta_labels(db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    rows = await db.execute(
        select(Venta.id, Cliente.nombre, Cliente.apellido, Vehiculo.marca, Vehiculo.modelo, Vehiculo.patente)
        .join(Cliente, Venta.cliente_id == Cliente.id)
        .join(Vehiculo, Venta.vehiculo_id == Vehiculo.id)
        .order_by(Venta.fecha_venta.desc())
    )
    return [
        VentaLabel(
            id=row.id,
            label=f"{row.nombre} {row.apellido} · {row.marca} {row.modelo}"
            + (f" · {row.patente}" if row.patente else ""),
        )
        for row in rows
    ]


@router.get("/", response_model=List[VentaResponse])
async def list_ventas(db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    result = await db.execute(select(Venta).order_by(Venta.fecha_venta.desc()))
    return result.scalars().all()


@router.get("/{id}", response_model=VentaResponse)
async def get_venta(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    v = await db.get(Venta, id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v


@router.post("/", response_model=VentaResponse, status_code=201)
async def create_venta(
    data: VentaCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    vehiculo = await db.get(Vehiculo, data.vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if vehiculo.estado != EstadoVehiculo.disponible:
        raise HTTPException(status_code=409, detail="El vehículo no está disponible")

    venta = Venta(**data.model_dump())
    db.add(venta)
    # The DB trigger will mark the vehicle as sold, but we also update here for consistency
    vehiculo.estado = EstadoVehiculo.vendido
    await db.commit()
    await db.refresh(venta)
    return venta


@router.put("/{id}", response_model=VentaResponse)
async def update_venta(
    id: int,
    data: VentaUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    v = await db.get(Venta, id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(v, field, val)
    await db.commit()
    await db.refresh(v)
    return v
