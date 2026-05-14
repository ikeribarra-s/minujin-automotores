import base64
import json
import logging
import time
from datetime import date, datetime

from anthropic import AsyncAnthropic
from backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM = """Sos un agente de procesamiento de documentos financieros integrado a una
aplicación web Python. Tu función principal es analizar imágenes de cheques
y pagarés argentinos, extraer sus datos con precisión y registrarlos en la
base de datos del sistema.

## Tu rol
Cuando recibís una imagen de un cheque o pagaré, debés:
1. Identificar si es un cheque bancario (Santander, Banco Nación, Macro, etc.) o un pagaré.
2. Extraer todos los campos visibles con la mayor fidelidad posible.
3. Estructurar los datos en formato JSON y confirmar el registro en la base de datos.

## Campos a extraer
- tipo: "cheque" o "pagare"
- banco: nombre del banco emisor (si aplica)
- numero: número de cheque o pagaré
- monto_numerico: importe en números (ej: 45368.46)
- monto_letras: importe escrito en letras tal como figura en el documento
- fecha_emision: fecha en formato DD/MM/YYYY
- fecha_vencimiento: fecha en formato DD/MM/YYYY
- pagador_nombre: nombre o razón social del firmante
- pagador_cuit: CUIT del firmante si está visible
- beneficiario: nombre de quien cobra
- sucursal: sucursal bancaria si figura
- localidad: localidad del documento
- es_cpd: true si es cheque de pago diferido, false si es al día
- discrepancia_monto: true si el monto en números no coincide con el escrito en letras

## Reglas de extracción
- Si un campo no es legible o no figura, devolvé null para ese campo.
- El monto_numerico debe ser siempre un número (sin símbolos de moneda ni puntos de miles).
- Las fechas deben normalizarse siempre a DD/MM/YYYY aunque estén escritas en texto.
- Si hay discrepancia entre el monto en números y el monto en letras, marcá discrepancia_monto: true.
- En pagarés, el campo banco va como null.

## Formato de respuesta
Siempre respondé con un JSON válido. No incluyas texto adicional, backticks ni explicaciones fuera del JSON.

## Contexto del sistema
- Los registros se guardan en una base de datos relacional asociada a cobros y pagos.
- El sistema opera en Argentina; los montos son en pesos argentinos (ARS)."""


_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or None)
    return _client


def _parse_date(val: str | None) -> date | None:
    if not val:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


async def extract_fields(ocr_text: str, image_bytes: bytes) -> dict:
    client = _get_client()
    t0 = time.time()
    b64 = base64.standard_b64encode(image_bytes).decode()

    response = await client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Texto OCR extraído del documento:\n<ocr_text>\n{ocr_text}\n</ocr_text>\n\n"
                        "Analizá también la imagen adjunta para confirmar o corregir el texto OCR."
                    ),
                },
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                },
            ],
        }],
    )

    raw_text = response.content[0].text
    logger.info("Claude extraction: %.2fs", time.time() - t0)

    try:
        fields = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("Claude returned non-JSON: %s", raw_text[:300])
        return {"error": "parse_failed", "raw": raw_text}

    for key in ("fecha_emision", "fecha_vencimiento"):
        if key in fields and fields[key]:
            parsed = _parse_date(fields[key])
            fields[key] = parsed.isoformat() if parsed else None

    return fields


def get_anthropic_client() -> AsyncAnthropic:
    return _get_client()
