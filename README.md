# apate
**Apate** is an open-source tool to detect AI-generated and deepfake videos using spatiotemporal and multimodal learning. with frame-level heatmaps. Built for generalization across generators like Sora, Pika, Runway, and more.

## Features
- Frame & video-level detection
- Heatmap visualization with CAMs
- Modular model integration (CNN-RNN, transformers, etc.)
- CLI + Dashboard support

##  Video Analysis API & Dashboard


This module adds a FastAPI + Celery pipeline for **async video analysis** with FFmpeg normalization, frame extraction, a demo classifier, and Grad-CAM heatmaps. It also includes a small React uploader and Docker orchestration.

### Services (Docker Compose)

*   **api**: FastAPI app on `http://localhost:8000`
*   **redis**: Broker for Celery
*   **worker**: Celery worker running the video pipeline
*   **static**: Nginx serving artifacts at `http://localhost:8080`

### Quick Start (Docker)

1.  Ensure Docker & Docker Compose are installed, and `ffmpeg` is available inside the containers (already included).
2.  From the repo root, run:

    docker compose up --build

After it starts:  
• API docs (Swagger): `http://localhost:8000/docs`  
• Static results browser: `http://localhost:8080/`

### Environment Variables (safe defaults)

Variable

Default

Description

`MAX_UPLOAD_MB`

200

Max file size in MB (HTTP 413 on exceed)

`ALLOWED_EXTS`

mp4,mov,mkv,webm,avi,flv

Allowed extensions

`DEFAULT_FPS`

1.0

Frames per second for extraction (configurable per job)

`RESULTS_DIR`

results

Artifacts output directory

`UPLOADS_DIR`

uploads

Upload staging directory

`BASE_EXTERNAL_URL`

http://localhost:8000

Base URL used in status/result links

`REDIS_URL`

redis://redis:6379/0

Redis connection

`CELERY_BROKER_URL`

redis://redis:6379/0

Celery broker

`CELERY_RESULT_BACKEND`

redis://redis:6379/0

Celery result backend

### API Endpoints

*   **POST** `/api/upload`
    
    _Form-data_:
    
    *   `file` _(optional)_ — one of: mp4, mov, mkv, webm, avi, flv
    *   `url` _(optional)_ — http/https link to video
    *   `fps` _(optional)_ — override default fps
    
    _Response_: `{ "job_id": "...", "status_url": "..." }`
    
    _Errors_: 400 missing input, 413 too large, 415 bad type
    
*   **GET** `/api/status/{job_id}`
    
    Return job `status` (queued|running|succeeded|failed), `progress`, `error?`, and `result_url?`.
    
*   **GET** `/api/result/{job_id}`
    
    Return final JSON with overall prediction, per-frame scores, heatmap paths, timestamps, and artifacts (normalized video URL).
    

### Processing Pipeline

1.  Accept upload or download URL (size & extension validation; 200 MB default limit)
2.  Enqueue Celery job and return `job_id` immediately
3.  Transcode to canonical format (H.264/AAC, 720p) via FFmpeg
4.  Extract frames at configured FPS (default 1)
5.  Run demo video-level classifier (ResNet18 proxy) and compute Grad-CAM heatmaps per frame
6.  Write `result.json` with: overall score/label, per-frame scores, heatmap URLs (`/static/<job_id>/heatmaps/...`), timestamps

### Local Development (without Docker)

1.  Install Python 3.11 and `ffmpeg`.
2.  Setup venv and deps:

    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

3.  Start Redis locally (e.g., `docker run -p 6379:6379 redis:7`)
4.  Run API:

    export PYTHONPATH=.
    export REDIS_URL=redis://localhost:6379/0
    uvicorn apate.api.main:app --reload

5.  Run worker:

    celery -A apate.worker.celery_app.celery_app worker --loglevel=INFO

### Frontend (minimal React component)

A single-file uploader exists at `frontend/UploadWidget.jsx`. It supports drag-and-drop, file input, URL analysis, progress, polling, and heatmap gallery.

    // Example usage
    import UploadWidget from "./frontend/UploadWidget.jsx";
    export default function Page() {
      return <UploadWidget apiBase="http://localhost:8000" />;
    }

### CURL Examples

    # Upload local file
    curl -F "file=@/path/to/video.mp4" http://localhost:8000/api/upload
    
    # Upload by URL (with custom fps)
    curl -F "url=https://example.com/sample.mp4" -F "fps=2.0" http://localhost:8000/api/upload
    
    # Poll status
    curl http://localhost:8000/api/status/<job_id>
    
    # Get final result JSON
    curl http://localhost:8000/api/result/<job_id> | jq .
    

### Demo Script

Run the end-to-end demo once services are up:

    bash scripts/demo.sh

### Tests

Pytest includes validation tests for the upload endpoint and a smoke test that generates a 1-second video and runs the full Celery task.

    pytest -q

### Limitations & Next Steps

*   **Auth & Throttling**: Add API keys / OAuth and per-IP rate limits.
*   **Input Hardening**: Validate MIME via `ffprobe`, sanitize URLs, restrict to http/https.
*   **Malware Scanning**: Consider ClamAV for untrusted uploads.
*   **Quotas**: Auto-clean old jobs; disk usage guardrails.
*   **Model Swap**: Replace demo ResNet18 proxy with your trained binary classifier and proper calibration.
*   **Observability**: Add metrics (Prometheus) and structured logs.
*   **GPU**: Provide CUDA base image & compose device requests when needed.
*   **Large Files**: Support resumable/chunked uploads if raising limits.

### Error Handling

*   Unsupported extension → `415` with friendly message.
*   File exceeds limit → `413` with friendly message.
*   Unknown job → `404`.
*   Failed job → `status=failed` and `error` string in `/api/status` (non-sensitive).

### Folder Layout

    apate/
      api/        # FastAPI endpoints & DB
      core/       # config, ffmpeg, model, explainability
      worker/     # Celery worker & tasks
      frontend/   # React UploadWidget.jsx
    results/      # artifacts (exposed via nginx)
    uploads/      # original uploads
    tests/        # pytest: API + smoke
    scripts/      # demo script