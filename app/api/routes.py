
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.responses import FileResponse

from app.core.url_validator import validate_social_url

from app.core.file_store import (
    ALLOWED_TYPES,
    MAX_FILE_BYTES,
    get_media,
    save_media,
)

from app.schemas.media import (
    HealthResponse,
    ValidateRequest,
    ValidateResponse,
)

from app.services.tiktok import resolve_tiktok_video


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
async def health_check():
    return {
        "status": "ok",
        "service": "VidNex Media API",
        "version": "1.0.0",
    }


@router.post(
    "/media/validate",
    response_model=ValidateResponse,
    tags=["Media"],
)
async def validate_media(payload: ValidateRequest):
    return validate_social_url(payload.url)


@router.post(
    "/media/resolve",
    tags=["Media"],
)
async def resolve_media(payload: ValidateRequest):
    validation = validate_social_url(payload.url)

    if validation["platform"].value != "tiktok":
        raise HTTPException(
            status_code=501,
            detail=(
                "Media retrieval for this platform "
                "is not available yet."
            ),
        )

    return await resolve_tiktok_video(
        validation["source_url"]
    )


@router.post(
    "/media/files",
    tags=["Media Storage"],
)
async def create_media_file(
    file: UploadFile = File(...),
):
    content_type = (file.content_type or "").lower()

    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type.",
        )

    data = await file.read(MAX_FILE_BYTES + 1)
    await file.close()

    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Media files must not exceed 50 MB.",
        )

    stored = save_media(
        data=data,
        content_type=content_type,
    )

    return {
        "success": True,
        "message": "Media file stored successfully.",
        "file": stored,
    }


@router.get(
    "/files/{file_id}",
    tags=["Media Storage"],
)
async def download_media_file(file_id: str):
    media = get_media(file_id)

    return FileResponse(
        path=media["path"],
        media_type=media["content_type"],
        filename=media["filename"],
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
