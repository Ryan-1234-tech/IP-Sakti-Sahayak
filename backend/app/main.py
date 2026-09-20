"""
app/main.py — FastAPI application entry point.

Mounts all routers under /api and handles:
  - CORS
  - Lifespan startup (DB init)
  - Health check endpoint
  - Global exception handler
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db
from app.routers import chat, document, features, feedback, profile, sources, tk_risk, upload


logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown tasks."""
    logger.info("🚀 IP-SAKTI Sahayak backend starting up…")

    # Initialise SQLite tables
    await init_db()
    logger.info("✅ Database ready.")

    # Pre-warm the embedding model (avoids cold-start latency on first request)
    try:
        from app.services.embeddings import embed_text

        embed_text("warm up")
        logger.info("✅ Embedding model loaded.")
    except Exception as e:
        logger.warning(f"⚠️  Embedding model pre-warm failed: {e}")

    yield  # application runs here

    logger.info("👋 IP-SAKTI Sahayak backend shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="IP-SAKTI Sahayak API",
    description=(
        "Grounded decision-support for Indian Intellectual Property and "
        "AYUSH regulatory guidance. Answers are cited, confidence-scored, "
        "and accompanied by actionable next steps."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again.", "code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["system"], summary="Health check")
@app.get("/api/health", tags=["system"], summary="Health check")
async def health():
    """Returns API status and basic diagnostics."""
    import httpx
    from app.services.vector_store import collection_count

    chunk_count = collection_count()
    provider = settings.llm_provider.lower().strip()
    ollama_connected = False
    active_model = settings.ollama_model

    if provider == "ollama":
        try:
            headers = {}
            if settings.ollama_api_key:
                headers["Authorization"] = f"Bearer {settings.ollama_api_key}"
            with httpx.Client(timeout=1.5) as client:
                r = client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", headers=headers)
                if r.status_code == 200:
                    ollama_connected = True
        except Exception:
            ollama_connected = False

    llm_configured = (provider == "ollama" and ollama_connected) or (
        provider == "anthropic" and bool(settings.anthropic_api_key)
    )

    if provider == "ollama":
        msg = (
            f"Ollama connected ({active_model})."
            if ollama_connected
            else f"Ollama not detected on {settings.ollama_base_url}. Start Ollama with 'ollama run {active_model}'."
        )
    else:
        msg = "Anthropic API ready." if bool(settings.anthropic_api_key) else "Anthropic API key not configured."

    return {
        "status": "ok",
        "version": "0.1.0",
        "llm_provider": provider,
        "llm_model": active_model if provider == "ollama" else settings.claude_model,
        "llm_configured": llm_configured,
        "kb_chunk_count": chunk_count,
        "message": msg,
    }



# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(document.router, prefix="/api", tags=["document"])
app.include_router(sources.router, prefix="/api", tags=["sources"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(tk_risk.router, prefix="/api", tags=["tk-risk"])
app.include_router(features.router, prefix="/api", tags=["features"])




