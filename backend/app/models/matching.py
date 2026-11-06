import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.core.database import Base

_DIMENSIONS = get_settings().matching_embedding_dimensions
_VECTOR_TYPE = Vector(_DIMENSIONS).with_variant(JSON(), "sqlite")


class MatchingEmbedding(Base):
    __tablename__ = "matching_embeddings"
    __table_args__ = (
        CheckConstraint(
            "(candidate_id IS NOT NULL AND job_id IS NULL) OR "
            "(candidate_id IS NULL AND job_id IS NOT NULL)",
            name="single_embedding_owner",
        ),
        Index(
            "uq_matching_embeddings_candidate_kind_model",
            "candidate_id",
            "embedding_kind",
            "model_name",
            unique=True,
            sqlite_where=text("candidate_id IS NOT NULL"),
            postgresql_where=text("candidate_id IS NOT NULL"),
        ),
        Index(
            "uq_matching_embeddings_job_kind_model",
            "job_id",
            "embedding_kind",
            "model_name",
            unique=True,
            sqlite_where=text("job_id IS NOT NULL"),
            postgresql_where=text("job_id IS NOT NULL"),
        ),
        Index(
            "ix_matching_embeddings_vector",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("candidate_profiles.id", ondelete="CASCADE")
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE")
    )
    embedding_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(_VECTOR_TYPE, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class MatchingResult(Base):
    __tablename__ = "matching_results"
    __table_args__ = (
        Index("ix_matching_results_candidate_created", "candidate_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    scoring_model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
