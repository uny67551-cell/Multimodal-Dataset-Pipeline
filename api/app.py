"""FastAPI entrypoint for Multimodal Dataset Pipeline."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # CORS middleware to allow requests from different origins

from api.deps import REPO_ROOT
from api.routes.reports import router as reports_router
from api.routes.images import router as images_router
from api.routes.uploads import router as uploads_router
from api.routes.pipeline import router as pipeline_router

os.chdir(REPO_ROOT)  # change the current working directory to the root of the repository

app = FastAPI(
    title="Multimodal Dataset Pipeline API",
    version="0.1.0",
    description="HTTP API over the existing pipeline stages and reports.",
)

# Vue dev server will call this API (different port) — allow local CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",  # Vue dev server will call this API (different port) — allow local CORS.
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (Authorization, Content-Type, etc.)
)

app.include_router(reports_router)  # include_router() comes from FastAPI, it is used to include a router in the main app
app.include_router(images_router)
app.include_router(uploads_router)
app.include_router(pipeline_router)

@app.get("/api/health") # get(), it is router function
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
