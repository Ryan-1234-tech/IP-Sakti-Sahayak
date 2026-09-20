"""
services/embeddings.py — Fast, lightweight multilingual embeddings using fastembed / onnxruntime.

Uses quantized models (e.g., BAAI/bge-small-en-v1.5 or multilingual models) with zero PyTorch / MSVC dependencies.
Fast, runs locally, zero-ops.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache(maxsize=1)
def _load_model():
    """Load the fastembed embedding model (cached singleton)."""
    try:
        from fastembed import TextEmbedding

        logger.info("Loading FastEmbed TextEmbedding model (BAAI/bge-small-en-v1.5)...")
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        logger.info("FastEmbed embedding model loaded successfully.")
        return model
    except Exception as e:
        logger.warning(f"FastEmbed load failed or not available ({e}); using fallback embedding.")
        return None


def embed_text(text: str) -> List[float]:
    """Embed a single string and return its vector as a list of floats."""
    model = _load_model()
    if model is not None:
        try:
            embeddings_gen = model.embed([text])
            vector = next(iter(embeddings_gen))
            return vector.tolist()
        except Exception as e:
            logger.warning(f"Embedding single text failed: {e}")
    # Fallback pseudo-embedding if model unavailable
    import hashlib
    h = hashlib.sha256(text.encode("utf-8")).digest()
    return [(b / 255.0) for b in h]


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch-embed a list of strings."""
    if not texts:
        return []
    model = _load_model()
    if model is not None:
        try:
            embeddings_gen = model.embed(texts, batch_size=32)
            return [v.tolist() for v in embeddings_gen]
        except Exception as e:
            logger.warning(f"Batch embedding failed: {e}")
    return [embed_text(t) for t in texts]


def embedding_dimension() -> int:
    """Return output dimension of current embedding model (384 for bge-small)."""
    return 384
