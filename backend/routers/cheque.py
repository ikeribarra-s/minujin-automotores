import json
import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from backend.database import get_db
from backend.auth import verify_token
from backend.models.cheque import Cheque
from backend.models.enums import EstadoCheque
from backend.schemas.cheque import ChequeCreate, ChequeUpdate, ChequeResponse, ScanResult
from backend.config import settings
from backend.scanner.utils import validate_and_prepare_image
from backend.scanner.ocr import extract_text_google_vision, extract_text_fallback, OCRError
from backend.scanner.extractor import extract_fields, get_anthropic_client

logger = logging.getLogger(__name__)

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


@router.post("/scan", response_model=ScanResult)
async def scan_cheque(
    file: UploadFile = File(...),
    _: str = Depends(verify_token),
):
    """Extract cheque/pagaré fields from an uploaded image. Does not write to DB."""
    raw_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"

    try:
        image_bytes = validate_and_prepare_image(raw_bytes, content_type, settings.MAX_UPLOAD_MB)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # OCR: try Google Vision, fall back to Claude vision
    ocr_text = ""
    warning = None
    anthropic_client = get_anthropic_client()

    try:
        ocr_text = await extract_text_google_vision(image_bytes)
        if not ocr_text.strip():
            logger.info("Google Vision returned empty text, falling back to Claude")
            ocr_text = await extract_text_fallback(image_bytes, anthropic_client)
            warning = "OCR via Claude (Google Vision returned vacío)"
    except OCRError as e:
        logger.warning("Google Vision failed (%s), falling back to Claude", e)
        try:
            ocr_text = await extract_text_fallback(image_bytes, anthropic_client)
            warning = "OCR via Claude (Google Vision no disponible)"
        except Exception as fallback_err:
            logger.error("OCR fallback also failed: %s", fallback_err)
            raise HTTPException(status_code=502, detail="No se pudo extraer texto de la imagen")

    # Extract structured fields with Claude
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
        warning=warning,
    )
