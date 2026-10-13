
import re
import secrets
import time

from pathlib import Path

from fastapi import HTTPException


STORAGE_DIR = Path("storage/media")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_BYTES = 50 * 1024 * 1024
FILE_TTL_SECONDS = 1800

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "audio/mpeg": ".mp3",
}


def save_media(
    data: bytes,
    content_type: str,
) -> dict:
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported media format.",
        )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="The media file is empty.",
        )

    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Media files must not exceed 50 MB.",
        )

    file_id = secrets.token_hex(24)
    extension = ALLOWED_TYPES[content_type]
    expires_at = int(time.time()) + FILE_TTL_SECONDS

    filename = f"{file_id}{extension}"
    path = STORAGE_DIR / filename

    path.write_bytes(data)

    return {
        "file_id": file_id,
        "filename": filename,
        "content_type": content_type,
        "download_url": f"/api/v1/files/{file_id}",
        "expires_at": expires_at,
    }


def get_media(file_id: str):
    if not re.fullmatch(r"[a-f0-9]{48}", file_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid file ID.",
        )

    for content_type, extension in ALLOWED_TYPES.items():
        path = STORAGE_DIR / f"{file_id}{extension}"

        if not path.is_file():
            continue

        created_at = path.stat().st_mtime

        if time.time() - created_at > FILE_TTL_SECONDS:
            path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=410,
                detail="This download link has expired.",
            )

        return {
            "path": path,
            "content_type": content_type,
            "filename": f"vidnex-{file_id[:12]}{extension}",
        }

    raise HTTPException(
        status_code=404,
        detail="Media file not found.",
    )
