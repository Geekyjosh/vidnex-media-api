
import re

from urllib.parse import urlsplit, urlunsplit

from fastapi import HTTPException

from app.schemas.media import MediaType, Platform


ALLOWED_HOSTS = {
    Platform.TIKTOK: {
        "tiktok.com",
        "www.tiktok.com",
        "m.tiktok.com",
        "vt.tiktok.com",
        "vm.tiktok.com",
    },
    Platform.INSTAGRAM: {
        "instagram.com",
        "www.instagram.com",
    },
    Platform.FACEBOOK: {
        "facebook.com",
        "www.facebook.com",
        "m.facebook.com",
        "web.facebook.com",
        "fb.watch",
    },
    Platform.X: {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
        "mobile.twitter.com",
    },
}


def identify_platform(hostname: str) -> Platform:
    for platform, hosts in ALLOWED_HOSTS.items():
        if hostname in hosts:
            return platform

    raise HTTPException(
        status_code=400,
        detail="Unsupported social media platform.",
    )


def identify_media_type(
    platform: Platform,
    path: str,
) -> MediaType:
    if platform == Platform.TIKTOK:
        if re.fullmatch(
            r"/@[^/]+/photo/\d{10,25}/?",
            path,
        ):
            return MediaType.CAROUSEL

        if re.fullmatch(
            r"/@[^/]*/video/\d{10,25}/?",
            path,
        ):
            return MediaType.VIDEO

        if re.fullmatch(
            r"/v/\d{10,25}\.html/?",
            path,
        ):
            return MediaType.VIDEO

        if re.fullmatch(
            r"/embed/v2/\d{10,25}/?",
            path,
        ):
            return MediaType.VIDEO

        # Short links must be resolved before we can
        # determine their actual media type.
        if re.fullmatch(
            r"/[A-Za-z0-9_-]{3,100}/?",
            path,
        ):
            return MediaType.UNKNOWN

    if platform == Platform.INSTAGRAM:
        if re.fullmatch(r"/reel/[^/]+/?", path):
            return MediaType.VIDEO

        if re.fullmatch(r"/p/[^/]+/?", path):
            # Instagram posts can contain photos,
            # carousels, or videos.
            return MediaType.UNKNOWN

        if re.fullmatch(r"/tv/[^/]+/?", path):
            return MediaType.VIDEO

    if platform == Platform.FACEBOOK:
        if (
            "/videos/" in path
            or path.startswith("/reel/")
            or path.startswith("/watch")
        ):
            return MediaType.VIDEO

        return MediaType.UNKNOWN

    if platform == Platform.X:
        if re.fullmatch(
            r"/(?:i/web|[^/]+)/status/\d+/?",
            path,
        ):
            # A post may contain videos, photos,
            # or no media at all.
            return MediaType.UNKNOWN

    return MediaType.UNKNOWN


def validate_social_url(value: str) -> dict:
    raw = value.strip()

    try:
        parsed = urlsplit(raw)

        if (
            parsed.scheme.lower() != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
        ):
            raise ValueError("Invalid URL.")

        hostname = parsed.hostname.lower()
        platform = identify_platform(hostname)

        if len(raw) > 2048:
            raise ValueError("URL is too long.")

        # Remove fragment but preserve path and query.
        clean_url = urlunsplit(
            (
                "https",
                hostname,
                parsed.path or "/",
                parsed.query,
                "",
            )
        )

        media_type = identify_media_type(
            platform,
            parsed.path or "/",
        )

        if media_type == MediaType.UNKNOWN:
            message = (
                "Platform recognized. Media type "
                "requires further verification."
            )
        else:
            message = (
                f"URL format recognized as "
                f"{media_type.value}."
            )

        return {
            "success": True,
            "platform": platform,
            "media_type": media_type,
            "source_url": clean_url,
            "message": message,
        }

    except HTTPException:
        raise

    except (ValueError, OverflowError):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid HTTPS social media URL.",
        )
