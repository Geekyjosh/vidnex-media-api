# VidNex Media API

**A Python-based REST API for media resolution, processing, and file delivery.**

VidNex Media API is a backend service built with **Python, FastAPI, and yt-dlp** to process supported media URLs, retrieve authorized media content, and provide temporary downloadable files through a RESTful interface.

The project serves as the backend foundation for **VidNex**, a web application for working with video and image content from supported social media platforms.

## Features

### Implemented

- **RESTful API:** Backend endpoints built with FastAPI.
- **URL Validation:** Recognition of supported TikTok, Instagram, Facebook, and X URL formats.
- **TikTok Video Processing:** Video retrieval using yt-dlp for supported, authorized content.
- **Media Metadata:** Extract video titles, creator information, thumbnails, and video IDs.
- **Temporary File Storage:** Store downloaded media locally with automatically expiring download links.
- **File Downloads:** Deliver MP4 and supported media files through dedicated API endpoints.
- **File Validation:** Enforce supported media types and file-size limits.
- **Interactive API Documentation:** Automatically generated Swagger UI and OpenAPI schema.
- **Error Handling:** Structured responses for invalid URLs, unsupported content, and processing errors.
- **Asynchronous API:** FastAPI endpoints with video processing delegated to worker threads.

### Planned

- TikTok photo and carousel extraction
- Individual image downloads
- Download All Images without ZIP archives
- Image-to-MP4 slideshow conversion using FFmpeg
- Instagram, Facebook, and X media adapters
- Integration with the VidNex Next.js frontend
- API authentication and rate limiting
- Background processing and job tracking
- Persistent object storage
- Docker support, automated testing, and production deployment

## Technology Stack

| Technology        | Purpose                            |
| ----------------- | ---------------------------------- |
| Python            | Backend programming language       |
| FastAPI           | REST API framework                 |
| yt-dlp            | Supported media extraction         |
| Pydantic          | Request validation and data models |
| Uvicorn           | ASGI application server            |
| Python Multipart  | Multipart file uploads             |
| Swagger / OpenAPI | Interactive API documentation      |
| Local Filesystem  | Temporary media storage            |

## Project Structure

```text
vidnex-media-api/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── file_store.py
│   │   └── url_validator.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── media.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── tiktok.py
│   ├── __init__.py
│   └── main.py
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Geekyjosh/vidnex-media-api.git
cd vidnex-media-api
```

### 2. Create a virtual environment

On Windows using Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the development server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at:

`http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation.

**Swagger UI**

`http://localhost:8000/docs`

**ReDoc**

`http://localhost:8000/redoc`

**OpenAPI Schema**

`http://localhost:8000/openapi.json`

## API Endpoints

| Method | Endpoint                  | Description                                         |
| ------ | ------------------------- | --------------------------------------------------- |
| GET    | `/`                       | API information                                     |
| GET    | `/api/v1/health`          | Service health check                                |
| POST   | `/api/v1/media/validate`  | Validate and classify a media URL                   |
| POST   | `/api/v1/media/resolve`   | Resolve and retrieve supported TikTok video content |
| POST   | `/api/v1/media/files`     | Store an uploaded media file (development only)     |
| GET    | `/api/v1/files/{file_id}` | Download a temporarily stored file                  |

### Example: Health Check

**Request**

```http
GET /api/v1/health
```

**Response**

```json
{
  "status": "ok",
  "service": "VidNex Media API",
  "version": "1.0.0"
}
```

### Example: Validate a Media URL

**Request**

```http
POST /api/v1/media/validate
Content-Type: application/json
```

```json
{
  "url": "https://www.tiktok.com/@creator/video/7694805183229971718"
}
```

**Example response**

```json
{
  "success": true,
  "platform": "tiktok",
  "media_type": "video",
  "source_url": "https://www.tiktok.com/@creator/video/7694805183229971718",
  "message": "URL format recognized as video."
}
```

URL validation identifies supported link formats. It does not guarantee that the referenced content exists or can be downloaded.

### Example: Resolve a TikTok Video

**Request**

```http
POST /api/v1/media/resolve
Content-Type: application/json
```

```json
{
  "url": "https://vt.tiktok.com/ZSbwq9pou/"
}
```

**Example successful response (abbreviated)**

```json
{
  "success": true,
  "type": "video",
  "platform": "tiktok",
  "title": "Example TikTok video",
  "author": "examplecreator",
  "thumbnail": "https://example.com/thumbnail.jpg",
  "source_url": "https://vt.tiktok.com/ZSbwq9pou/",
  "video_id": "7694805183229971718",
  "download_available": true,
  "file": {
    "file_id": "generated-file-id",
    "filename": "generated-filename.mp4",
    "content_type": "video/mp4",
    "download_url": "/api/v1/files/generated-file-id",
    "expires_at": 1790000000
  }
}
```

Response values above are illustrative. Actual results depend on the submitted video and its availability.

### Example: Download a File

```http
GET /api/v1/files/{file_id}
```

The endpoint returns the stored media as a downloadable attachment.

Download links currently expire after approximately **30 minutes**.

## How It Works

```text
Client Application
       |
       v
FastAPI REST Endpoint
       |
       v
URL Validation
       |
       v
Platform Identification
       |
       v
TikTok Media Resolver
       |
       v
yt-dlp Extraction
       |
       v
Media File Validation
       |
       v
Temporary File Storage
       |
       v
Download URL
       |
       v
Client Downloads Media
```

## Media Handling

The API currently supports these stored-file formats:

- MP4 video
- MP3 audio
- JPEG images
- PNG images
- WebP images
- GIF images

The initial storage implementation limits files to **50 MB** each and uses a temporary local directory.

Support for storing a file format does not necessarily mean the API can extract that format from a social media post yet.

## Development Status

VidNex Media API is currently in **active development**.

The TikTok video retrieval workflow has been tested locally, including successful extraction, temporary storage, and MP4 download.

Other platform adapters, photo extraction, slideshow conversion, and production infrastructure are still under development.

**Security:** The current file-upload and media-resolution endpoints are development-stage implementations. Authentication, quotas, rate limiting, automated file cleanup, and durable storage must be added before public deployment.

## Responsible Usage

VidNex Media API is intended for media that users own or are authorized to access and download.

Users are responsible for respecting copyright, creator permissions, platform terms, and applicable laws. The project does not guarantee access to private, protected, or otherwise restricted media.

## Related Project

**VidNex Web Application**

Frontend repository: https://github.com/Geekyjosh/vidnex

The frontend uses Next.js, React, TypeScript, and Tailwind CSS.

## Author

**Olaoluwa Joshua Daramola**

Full-Stack Software Engineer

- GitHub: https://github.com/Geekyjosh
- Portfolio: https://josh-darams.vercel.app/

---

Built with Python and FastAPI. Part of the VidNex project ecosystem.

## License

Copyright © 2026 Olaoluwa Joshua Daramola. All Rights Reserved.

VidNex Media API is proprietary, source-available software.

The source code is publicly available for viewing and evaluation only. Copying, modification, redistribution, deployment, and commercial use are prohibited without prior written permission.

See the [LICENSE](LICENSE) file for complete terms.
