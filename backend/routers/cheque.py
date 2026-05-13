from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from backend.database import get_db
from backend.auth import verify_token
from backend.models.cheque import Cheque
from backend.models.enums import EstadoCheque
from backend.schemas.cheque import ChequeCreate, ChequeUpdate, ChequeResponse

router = APIRouter(prefix="/cheques", tags=["Cheques"])


@router.get("/", response_model=List[ChequeResponse])
async def list_cheques(
    estado: Optional[EstadoCheque] = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = select(Cheque)
    if estado:
        q = q.where(Cheque.estado == estado)
    result = await db.execute(q.order_by(Cheque.fecha_cobro))
    return result.scalars().all()


@router.get("/{id}", response_model=ChequeResponse)
async def get_cheque(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    c = await db.get(Cheque, id)
    if not c:
        raise HTTPException(status_code=404, detail="Cheque no encontrado")
    return c


@router.post("/", response_model=ChequeResponse, status_code=201)
async def create_cheque(
    data: ChequeCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    cheque = Cheque(**data.model_dump())
    db.add(cheque)
    await db.commit()
    await db.refresh(cheque)
    return cheque


@router.patch("/{id}", response_model=ChequeResponse)
async def update_cheque(
    id: int,
    data: ChequeUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    c = await db.get(Cheque, id)
    if not c:
        raise HTTPException(status_code=404, detail="Cheque no encontrado")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(c, field, val)
    await db.commit()
    await db.refresh(c)
    return c
