"""FastAPI entrypoint for Multimodal Dataset Pipeline."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import REPO_ROOT
from api.routes.reports import router as reports_router
from api.routes.images import router as images_router
from api.routes.uploads import router as uploads_router
from api.routes.pipeline import router as pipeline_router

os.chdir(REPO_ROOT)

app = FastAPI(
    title="Multimodal Dataset Pipeline API",
    version="0.1.0",
    description="HTTP API over the existing pipeline stages and reports.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)
app.include_router(images_router)
app.include_router(uploads_router)
app.include_router(pipeline_router)

@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
