"""
models/db.py — SQLAlchemy ORM table definitions.

Tables:
  - Source          : Knowledge base documents (seeded by ingest.py)
  - Conversation    : A chat session
  - Message         : Individual messages within a conversation
  - UploadedDocument: User-uploaded PDFs
  - BusinessProfile : MSME / Startup profile and IP portfolio
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Source(Base):
    """A curated knowledge-base document."""

    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=True)
    authority: Mapped[str] = mapped_column(String(256), nullable=True)  # e.g. "IP India", "WIPO", "Ministry of AYUSH"
    document_type: Mapped[str] = mapped_column(String(128), nullable=True)  # act/rule/guideline/treaty/faq
    jurisdiction: Mapped[str] = mapped_column(String(64), default="INDIA")  # INDIA | INTERNATIONAL
    topic: Mapped[str] = mapped_column(String(256), nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="en")
    publication_date: Mapped[str] = mapped_column(String(32), nullable=True)
    document_version: Mapped[str] = mapped_column(String(64), nullable=True)
    effective_date: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    """A chat session (may span multiple messages)."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    language: Mapped[str] = mapped_column(String(16), default="en")
    jurisdiction: Mapped[str] = mapped_column(String(64), default="INDIA")

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """A single turn in a conversation (user or assistant)."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # "user" | "assistant"
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON blobs — avoid extra normalised tables for a hackathon MVP
    sources_json: Mapped[str] = mapped_column(Text, default="[]")     # list[SourceRef]
    actions_json: Mapped[str] = mapped_column(Text, default="[]")     # list[Action]
    confidence: Mapped[str] = mapped_column(String(16), nullable=True)  # HIGH/MEDIUM/LOW
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)        # 1 = 👍, -1 = 👎
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )


class UploadedDocument(Base):
    """A PDF uploaded by the user for document intelligence."""

    __tablename__ = "uploaded_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    # JSON blob: {doc_type, summary, deadline_date, key_requirements}
    summary_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusinessProfile(Base):
    """Business Profile storing company metadata and IP asset portfolio."""

    __tablename__ = "business_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    company_name: Mapped[str] = mapped_column(String(256), nullable=False)
    sector: Mapped[str] = mapped_column(String(128), default="AYUSH")  # AYUSH, Pharma, Biotech, Software, MSME, etc.
    company_type: Mapped[str] = mapped_column(String(128), default="Startup")  # Startup, MSME, Enterprise, Researcher
    registration_number: Mapped[str] = mapped_column(String(128), nullable=True)  # UDYAM, CIN, License No
    state: Mapped[str] = mapped_column(String(128), nullable=True)
    # JSON blob: list of IPAsset [{asset_type, title, status, registration_no}]
    ip_assets_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
