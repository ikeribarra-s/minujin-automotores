import asyncio
import base64
import logging
import time

logger = logging.getLogger(__name__)


class OCRError(Exception):
    pass


async def extract_text_google_vision(image_bytes: bytes) -> str:
    try:
        from google.cloud import vision
    except ImportError:
        raise OCRError("google-cloud-vision no instalado")

    t0 = time.time()

    def _call() -> str:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image)
        if response.error.message:
            raise OCRError(f"Google Vision error: {response.error.message}")
        return response.full_text_annotation.text

    try:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _call)
        logger.info("Google Vision OCR: %.2fs, %d chars", time.time() - t0, len(text))
        return text
    except OCRError:
        raise
    except Exception as e:
        raise OCRError(str(e)) from e


async def extract_text_fallback(image_bytes: bytes, client) -> str:
    """Use Claude vision to transcribe when Google Vision is unavailable."""
    from anthropic import AsyncAnthropic

    t0 = time.time()
    b64 = base64.standard_b64encode(image_bytes).decode()
    response = await client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                },
                {
                    "type": "text",
                    "text": (
                        "Transcribe every visible character in this document image exactly as written, "
                        "preserving line breaks. Return only the raw transcription, nothing else."
                    ),
                },
            ],
        }],
    )
    text = response.content[0].text
    logger.info("Claude OCR fallback: %.2fs, %d chars", time.time() - t0, len(text))
    return text
