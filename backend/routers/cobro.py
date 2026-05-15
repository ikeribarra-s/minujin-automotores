from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from backend.database import get_db
from backend.auth import verify_token
from backend.models.cobro import Cobro
from backend.models.venta import Venta
from backend.schemas.cobro import CobroCreate, CobroUpdate, CobroResponse

router = APIRouter(prefix="/cobros", tags=["Cobros"])


@router.get("/", response_model=List[CobroResponse])
async def list_cobros(
    venta_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = select(Cobro)
    if venta_id:
        q = q.where(Cobro.venta_id == venta_id)
    result = await db.execute(q.order_by(Cobro.fecha.desc()))
    return result.scalars().all()


@router.get("/{id}", response_model=CobroResponse)
async def get_cobro(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    c = await db.get(Cobro, id)
    if not c:
        raise HTTPException(status_code=404, detail="Cobro no encontrado")
    return c


@router.post("/", response_model=CobroResponse, status_code=201)
async def create_cobro(
    data: CobroCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    venta = await db.get(Venta, data.venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    total_cobrado = await db.scalar(
        select(func.coalesce(func.sum(Cobro.monto), 0)).where(Cobro.venta_id == data.venta_id)
    )
    if total_cobrado + data.monto > venta.precio_final:
        raise HTTPException(
            status_code=400,
            detail=f"El cobro supera el precio final. Saldo pendiente: {venta.precio_final - total_cobrado}",
        )

    cobro = Cobro(**data.model_dump())
    db.add(cobro)
    await db.commit()
    await db.refresh(cobro)
    return cobro


@router.patch("/{id}", response_model=CobroResponse)
async def update_cobro(
    id: int,
    data: CobroUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    c = await db.get(Cobro, id)
    if not c:
        raise HTTPException(status_code=404, detail="Cobro no encontrado")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(c, field, val)
    await db.commit()
    await db.refresh(c)
    return c
