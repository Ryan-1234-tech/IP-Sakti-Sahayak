"""
services/vector_store.py — High performance local vector store using FAISS & numpy.

Features:
  - FAISS cosine similarity index
  - Local persistent storage (saved to json/pickle in persist dir)
  - Full metadata preservation (source_id, authority, jurisdiction, section, article, rule, page, url, etc.)
  - Jurisdiction filtering & prioritization (INDIA / INTERNATIONAL)
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.config import get_settings
from app.services.embeddings import embed_text, embed_texts

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RetrievedChunk:
    """A chunk returned from similarity search preserving authoritative provenance."""

    chunk_id: str
    text: str
    score: float  # cosine similarity normalized to [0, 1]
    metadata: Dict[str, Any]

    @property
    def source_id(self) -> Optional[str]:
        return self.metadata.get("source_id") or self.metadata.get("id")

    @property
    def source_title(self) -> str:
        return self.metadata.get("document_title") or self.metadata.get("title") or "Official Document"

    @property
    def title(self) -> str:
        return self.source_title

    @property
    def source_url(self) -> Optional[str]:
        return self.metadata.get("source_url") or self.metadata.get("url")

    @property
    def authority(self) -> Optional[str]:
        auth = self.metadata.get("authority")
        if auth:
            return auth
        # Derive authority from document_title or filename if missing
        title = (self.source_title or "").lower()
        if "ayush" in title or "ayurved" in title or "siddha" in title or "unani" in title:
            return "Ministry of AYUSH"
        elif "wipo" in title or "pct" in title or "patent cooperation treaty" in title:
            return "WIPO"
        elif "biodiversity" in title or "nba" in title:
            return "National Biodiversity Authority"
        elif "patent" in title or "trademark" in title or "copyright" in title or "design" in title or "gi" in title:
            return "IP India"
        return "Official Government Authority"

    @property
    def source_type(self) -> Optional[str]:
        return self.metadata.get("source_type") or self.metadata.get("document_type") or "guideline"

    @property
    def jurisdiction(self) -> str:
        j = self.metadata.get("jurisdiction")
        if j:
            return j.upper()
        # Derive jurisdiction from authority/title
        auth = (self.authority or "").lower()
        title = (self.source_title or "").lower()
        if "wipo" in auth or "wipo" in title or "pct" in title or "uspto" in title or "epo" in title or "international" in title:
            return "INTERNATIONAL"
        return "INDIA"

    @property
    def section(self) -> Optional[str]:
        return self.metadata.get("section")

    @property
    def article(self) -> Optional[str]:
        return self.metadata.get("article")

    @property
    def rule(self) -> Optional[str]:
        return self.metadata.get("rule")

    @property
    def page_number(self) -> Optional[int]:
        p = self.metadata.get("page_number") or self.metadata.get("page")
        if p is not None:
            try:
                return int(p)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def document_version(self) -> Optional[str]:
        return self.metadata.get("document_version") or self.metadata.get("version")

    @property
    def effective_date(self) -> Optional[str]:
        return self.metadata.get("effective_date") or self.metadata.get("publication_date")

    @property
    def is_primary_source(self) -> bool:
        """True if the source is a primary government source (Act, Rule, Gazette, Treaty, Manual)."""
        dt = (self.source_type or "").lower()
        return dt not in {"faq", "secondary", "blog", "informal"}


class LocalFAISSVectorStore:
    def __init__(self, persist_dir: str):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.persist_dir / "faiss.index"
        self.meta_file = self.persist_dir / "documents.json"

        self.ids: List[str] = []
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.index = None

        self._load()

    def _load(self):
        try:
            import faiss

            if self.meta_file.exists():
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ids = data.get("ids", [])
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])

            if self.index_file.exists() and len(self.ids) > 0:
                self.index = faiss.read_index(str(self.index_file))
                logger.info(f"Loaded FAISS index with {len(self.ids)} documents.")
        except Exception as e:
            logger.warning(f"Could not load existing index ({e}), starting fresh.")
            self.ids, self.documents, self.metadatas = [], [], []
            self.index = None

    def _save(self):
        try:
            import faiss

            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"ids": self.ids, "documents": self.documents, "metadatas": self.metadatas},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))
        except Exception as e:
            logger.error(f"Failed to persist FAISS index: {e}")

    def add_documents(
        self,
        ids: List[str],
        texts: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if not ids:
            return
        import faiss

        embeddings = np.array(embed_texts(texts), dtype=np.float32)
        # Normalize vectors for cosine similarity (Inner Product on normalized vectors)
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(embeddings)
        self.ids.extend(ids)
        self.documents.extend(texts)
        self.metadatas.extend(metadatas)

        self._save()
        logger.info(f"Added {len(ids)} documents to FAISS vector store. Total: {len(self.ids)}")

    def similarity_search(
        self,
        query: str,
        top_k: int = 6,
        where: Optional[Dict[str, Any]] = None,
        jurisdiction: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        if self.index is None or len(self.ids) == 0:
            return []

        import faiss

        query_vec = np.array([embed_text(query)], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        # Retrieve more candidates if filtering by metadata or jurisdiction
        fetch_k = min(len(self.ids), max(top_k * 4, 30))
        distances, indices = self.index.search(query_vec, fetch_k)

        chunks: List[RetrievedChunk] = []
        target_jur = jurisdiction.upper().strip() if jurisdiction else None

        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.ids):
                continue
            meta = self.metadatas[idx] if idx < len(self.metadatas) else {}

            # Metadata filter check
            if where:
                match = all(meta.get(k) == v for k, v in where.items())
                if not match:
                    continue

            # In Inner Product on normalized vectors, score is in [-1, 1], normalize to [0, 1]
            score = float(max(0.0, min(1.0, (dist + 1.0) / 2.0)))
            chunk = RetrievedChunk(
                chunk_id=self.ids[idx],
                text=self.documents[idx],
                score=score,
                metadata=meta,
            )

            # Jurisdiction filter
            if target_jur:
                chunk_jur = chunk.jurisdiction.upper()
                if target_jur == "INDIA" and chunk_jur != "INDIA":
                    continue
                elif target_jur == "INTERNATIONAL" and chunk_jur != "INTERNATIONAL":
                    continue

            chunks.append(chunk)
            if len(chunks) >= top_k:
                break

        return chunks

    def count(self) -> int:
        return len(self.ids)


DEFAULT_STATUTORY_SEEDS = [
    {
        "id": "seed-patent-sec3p",
        "text": "Section 3(p) of the Patents Act, 1970 provides that an invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not an invention within the meaning of this Act. Traditional Knowledge Digital Library (TKDL) and Ayurvedic Pharmacopoeia of India (API) references are cited to object to non-patentable traditional formulations. Form 18 examination requests and Form 1 and Form 2 filings are required.",
        "metadata": {
            "source_id": "indian-patents-act-1970",
            "document_title": "The Patents Act, 1970 (Act No. 39 of 1970)",
            "authority": "Indian Patent Office / Ministry of Commerce and Industry",
            "source_type": "statute",
            "jurisdiction": "INDIA",
            "section": "Section 3(p)",
            "page_number": 14,
            "document_version": "2024 Amendment",
            "effective_date": "1972-04-20",
            "source_url": "https://ipindia.gov.in/patents-act.htm",
        },
    },
    {
        "id": "seed-bda-sec6",
        "text": "Section 6(1) of the Biological Diversity Act, 2002 mandates that no person shall apply for any intellectual property right, by whatever name called, in or outside India for any invention based on any research or information on a biological resource obtained from India without obtaining the previous approval of the National Biodiversity Authority (NBA, Chennai) prior to the grant of patent via Form III. Section 3 applies to foreign entities and Section 7 requires SBB intimation.",
        "metadata": {
            "source_id": "biological-diversity-act-2002",
            "document_title": "Biological Diversity Act, 2002 & ABS Guidelines",
            "authority": "National Biodiversity Authority (NBA)",
            "source_type": "statute",
            "jurisdiction": "INDIA",
            "section": "Section 6",
            "rule": "Rule 18",
            "page_number": 8,
            "document_version": "2023 Amendment",
            "effective_date": "2003-04-15",
            "source_url": "http://nbaindia.org",
        },
    },
    {
        "id": "seed-ayush-rule158b",
        "text": "Rule 158B of Drugs and Cosmetics Rules, 1945 outlines licensing requirements for Ayurvedic, Siddha, and Unani (ASU) medicines. Classical ASU medicines require citation of 54 First Schedule texts. Patent or Proprietary ASU formulations require safety study evidence, published pilot clinical trials, and stability data under Form 25-D.",
        "metadata": {
            "source_id": "drugs-and-cosmetics-rules-1945",
            "document_title": "Drugs and Cosmetics Rules, 1945 (Rule 158B)",
            "authority": "Ministry of AYUSH / Central Drugs Standard Control Organisation",
            "source_type": "regulation",
            "jurisdiction": "INDIA",
            "rule": "Rule 158B",
            "page_number": 45,
            "document_version": "2022 Revision",
            "source_url": "https://ayush.gov.in",
        },
    },
    {
        "id": "seed-pct-trips",
        "text": "Article 27 of the WTO TRIPS Agreement sets patentable subject matter standards across all fields of technology for new inventions involving an inventive step. The Patent Cooperation Treaty (PCT) Article 22 provides a 30-month / 31-month timeline for international applicants to enter national phase examination before destination patent offices such as USPTO, EPO, and JPO.",
        "metadata": {
            "source_id": "wto-trips-pct-agreements",
            "document_title": "WTO TRIPS Agreement & WIPO Patent Cooperation Treaty (PCT)",
            "authority": "World Intellectual Property Organization (WIPO) / WTO",
            "source_type": "treaty",
            "jurisdiction": "INTERNATIONAL",
            "article": "Article 27 TRIPS / Article 22 PCT",
            "page_number": 1,
            "source_url": "https://www.wipo.int/pct",
        },
    },
]

_store: Optional[LocalFAISSVectorStore] = None


def _get_store() -> LocalFAISSVectorStore:
    global _store
    if _store is None:
        _store = LocalFAISSVectorStore(settings.chroma_persist_dir)
        if _store.count() == 0:
            _store.add_documents(
                ids=[s["id"] for s in DEFAULT_STATUTORY_SEEDS],
                texts=[s["text"] for s in DEFAULT_STATUTORY_SEEDS],
                metadatas=[s["metadata"] for s in DEFAULT_STATUTORY_SEEDS],
            )
    return _store


def add_documents(
    ids: List[str],
    texts: List[str],
    metadatas: List[Dict[str, Any]],
) -> None:
    _get_store().add_documents(ids, texts, metadatas)


def similarity_search(
    query: str,
    top_k: Optional[int] = None,
    where: Optional[Dict[str, Any]] = None,
    jurisdiction: Optional[str] = None,
) -> List[RetrievedChunk]:
    k = top_k or settings.retrieval_top_k
    return _get_store().similarity_search(query, top_k=k, where=where, jurisdiction=jurisdiction)


def collection_count() -> int:
    return _get_store().count()
