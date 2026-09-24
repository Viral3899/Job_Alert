"""FastAPI server for local development - runs on port 8001.

Provides /api/cron endpoint that can be called by external schedulers.
"""

import os
import sys
from pathlib import Path
from typing import Any

import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request, Response

from api.cron import handler
from logging_config import logger

app = FastAPI(title="Job Monitor API", version="4.0.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "job-monitor"}


@app.api_route("/api/cron", methods=["GET", "POST"])
async def cron_endpoint(request: Request) -> Response:
    """Cron endpoint called by external schedulers every 15 minutes."""
    result: dict[str, Any] = handler(request)
    return Response(content=result.get("body", ""), status_code=result.get("statusCode", 200))


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8001"))
    logger.info(f"Starting Job Monitor API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
