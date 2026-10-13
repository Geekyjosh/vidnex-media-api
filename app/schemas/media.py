
from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    X = "x"


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    UNKNOWN = "unknown"


class ValidateRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class ValidateResponse(BaseModel):
    success: bool
    platform: Platform
    media_type: MediaType
    source_url: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
