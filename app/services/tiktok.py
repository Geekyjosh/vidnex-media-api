
import asyncio
import logging
import tempfile

from pathlib import Path
from typing import Any

from fastapi import HTTPException
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.core.file_store import (
    MAX_FILE_BYTES,
    save_media,
)
from app.core.url_validator import validate_social_url
from app.schemas.media import MediaType, Platform


logger = logging.getLogger(__name__)

MAX_CONCURRENT_DOWNLOADS = 2
download_semaphore = asyncio.Semaphore(
    MAX_CONCURRENT_DOWNLOADS
)


def _download_tiktok_video(url: str) -> dict:
    with tempfile.TemporaryDirectory(
        prefix="vidnex-"
    ) as temporary_directory:
        download_dir = Path(temporary_directory)

        options: dict[str, Any] = {
            "format": (
                "best[ext=mp4][vcodec!=none]"
                "[acodec!=none]"
                "/best[ext=mp4][vcodec!=none]"
                "[acodec!=none]"
            ),
            "outtmpl": str(
                download_dir / "vidnex-video.%(ext)s"
            ),
            "noplaylist": True,
            "playlistend": 1,
            "ignoreerrors": False,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 15,
            "retries": 1,
            "fragment_retries": 1,
            "max_filesize": MAX_FILE_BYTES,
            "merge_output_format": "mp4",
            "restrictfilenames": True,
            "cachedir": False,
        }

        try:
            with YoutubeDL(options) as downloader:
                information = downloader.extract_info(
                    url,
                    download=True,
                )

        except DownloadError as exc:
            logger.warning(
                "TikTok extraction failed: %s",
                type(exc).__name__,
            )

            raise HTTPException(
                status_code=422,
                detail=(
                    "The video could not be retrieved. "
                    "It may be unavailable, unsupported, "
                    "or restricted."
                ),
            ) from exc

        if not isinstance(information, dict):
            raise HTTPException(
                status_code=422,
                detail="The extractor returned no video information.",
            )

        if information.get("_type") in {
            "playlist",
            "multi_video",
        }:
            raise HTTPException(
                status_code=422,
                detail="Multiple-video results are not supported yet.",
            )

        files = [
            file
            for file in download_dir.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".mp4"
        ]

        if len(files) != 1:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No complete MP4 file was produced "
                    "for this link."
                ),
            )

        video_path = files[0]

        if (
            video_path.stat().st_size == 0
            or video_path.stat().st_size > MAX_FILE_BYTES
        ):
            raise HTTPException(
                status_code=413,
                detail="The video exceeds the supported file limit.",
            )

        video_bytes = video_path.read_bytes()

        stored = save_media(
            data=video_bytes,
            content_type="video/mp4",
        )

        title = information.get("title")
        author = (
            information.get("uploader")
            or information.get("creator")
            or information.get("channel")
        )
        thumbnail = information.get("thumbnail")

        return {
            "success": True,
            "type": "video",
            "platform": "tiktok",
            "title": (
                title.strip()
                if isinstance(title, str) and title.strip()
                else "TikTok video"
            ),
            "author": (
                author.strip()
                if isinstance(author, str) and author.strip()
                else "TikTok creator"
            ),
            "thumbnail": (
                thumbnail
                if isinstance(thumbnail, str)
                and thumbnail.startswith("https://")
                else None
            ),
            "source_url": url,
            "video_id": str(
                information.get("id") or ""
            ),
            "download_available": True,
            "file": stored,
        }


async def resolve_tiktok_video(url: str) -> dict:
    validation = validate_social_url(url)

    if validation["platform"] != Platform.TIKTOK:
        raise HTTPException(
            status_code=501,
            detail=(
                "This platform's media resolver "
                "is not implemented yet."
            ),
        )

    if validation["media_type"] == MediaType.CAROUSEL:
        raise HTTPException(
            status_code=501,
            detail=(
                "TikTok photo posts are recognized, "
                "but photo extraction is not available yet."
            ),
        )

    async with download_semaphore:
        try:
            return await asyncio.to_thread(
                _download_tiktok_video,
                validation["source_url"],
            )
        except HTTPException:
            raise
        except Exception:
            logger.exception(
                "Unexpected TikTok media processing error"
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "An unexpected error occurred while "
                    "processing this media."
                ),
            )
