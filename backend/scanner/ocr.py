import asyncio
import base64
import logging
import time

logger = logging.getLogger(__name__)


class OCRError(Exception):
    pass


async def extract_text_claude(image_bytes: bytes, client) -> str:
    """Use Claude vision to transcribe the document image."""
    t0 = time.time()
    b64 = base64.standard_b64encode(image_bytes).decode()
    try:
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
    except Exception as e:
        raise OCRError(str(e)) from e

    text = response.content[0].text
    logger.info("Claude OCR: %.2fs, %d chars", time.time() - t0, len(text))
    return text
