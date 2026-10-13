
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse

from fastapi.exceptions import HTTPException

from app.api.routes import router


app = FastAPI(
    title="VidNex Media API",
    description=(
        "Backend API for social media URL validation, "
        "authorized media processing, and file delivery."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(
    router,
    prefix="/api/v1",
)


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "VidNex Media API",
        "status": "running",
        "docs": "/docs",
    }


@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )
