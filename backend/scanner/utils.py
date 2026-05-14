import io
from PIL import Image

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
_MAX_DIMENSION = 2000


def validate_and_prepare_image(file_bytes: bytes, content_type: str, max_mb: int = 10) -> bytes:
    if len(file_bytes) > max_mb * 1024 * 1024:
        raise ValueError(f"Imagen demasiado grande. Máximo {max_mb} MB.")
    if content_type not in _ALLOWED_MIME:
        raise ValueError(f"Tipo no permitido: {content_type}. Use JPEG, PNG o WebP.")
    try:
        buf = io.BytesIO(file_bytes)
        probe = Image.open(buf)
        probe.verify()
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception:
        raise ValueError("El archivo no es una imagen válida.")

    w, h = img.size
    if max(w, h) > _MAX_DIMENSION:
        ratio = _MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue()
