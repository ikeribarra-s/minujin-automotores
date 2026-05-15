import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from backend.database import get_db
from backend.auth import verify_token
from backend.models.pagare import Pagare
from backend.models.enums import EstadoPagare
from backend.schemas.pagare import PagareCreate, PagareUpdate, PagareResponse
from backend.schemas.cheque import ScanResult
from backend.config import settings
from backend.scanner.utils import validate_and_prepare_image
from backend.scanner.ocr import extract_text_claude, OCRError
from backend.scanner.extractor import extract_fields, get_anthropic_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagares", tags=["Pagarés"])


@router.get("/", response_model=List[PagareResponse])
async def list_pagares(
    estado: Optional[EstadoPagare] = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = select(Pagare)
    if estado:
        q = q.where(Pagare.estado == estado)
    result = await db.execute(q.order_by(Pagare.vencimiento))
    return result.scalars().all()


@router.get("/{id}", response_model=PagareResponse)
async def get_pagare(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_token)):
    p = await db.get(Pagare, id)
    if not p:
        raise HTTPException(status_code=404, detail="Pagaré no encontrado")
    return p


@router.post("/", response_model=PagareResponse, status_code=201)
async def create_pagare(
    data: PagareCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    pagare = Pagare(**data.model_dump())
    db.add(pagare)
    await db.commit()
    await db.refresh(pagare)
    return pagare


@router.patch("/{id}", response_model=PagareResponse)
async def update_pagare(
    id: int,
    data: PagareUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_token),
):
    p = await db.get(Pagare, id)
    if not p:
        raise HTTPException(status_code=404, detail="Pagaré no encontrado")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(p, field, val)
    await db.commit()
    await db.refresh(p)
    return p


@router.post("/scan", response_model=ScanResult)
async def scan_pagare(
    file: UploadFile = File(...),
    _: str = Depends(verify_token),
):
    """Extract pagaré fields from an uploaded image. Does not write to DB."""
    raw_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"

    try:
        image_bytes = validate_and_prepare_image(raw_bytes, content_type, settings.MAX_UPLOAD_MB)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    anthropic_client = get_anthropic_client()
    try:
        ocr_text = await extract_text_claude(image_bytes, anthropic_client)
    except OCRError as e:
        logger.error("Claude OCR failed: %s", e)
        raise HTTPException(status_code=502, detail="No se pudo extraer texto de la imagen")

    try:
        fields = await extract_fields(ocr_text, image_bytes)
    except Exception as e:
        logger.error("Claude extraction failed: %s", e)
        raise HTTPException(status_code=502, detail="Error al procesar el documento con IA")

    if "error" in fields:
        raise HTTPException(status_code=422, detail=f"No se pudo parsear la respuesta: {fields.get('raw', '')[:200]}")

    return ScanResult(
        tipo=fields.get("tipo"),
        banco=fields.get("banco"),
        numero=fields.get("numero"),
        monto_numerico=fields.get("monto_numerico"),
        monto_letras=fields.get("monto_letras"),
        fecha_emision=fields.get("fecha_emision"),
        fecha_vencimiento=fields.get("fecha_vencimiento"),
        pagador_nombre=fields.get("pagador_nombre"),
        pagador_cuit=fields.get("pagador_cuit"),
        beneficiario=fields.get("beneficiario"),
        sucursal=fields.get("sucursal"),
        localidad=fields.get("localidad"),
        es_cpd=fields.get("es_cpd", False) or False,
        discrepancia_monto=fields.get("discrepancia_monto", False) or False,
        raw_ocr_text=ocr_text,
        raw_json=fields,
        warning=None,
    )
