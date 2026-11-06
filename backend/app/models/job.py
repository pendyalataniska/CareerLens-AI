import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import CandidateProfile
    from app.models.recruiter import RecruiterProfile


class ApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    IN_REVIEW = "IN_REVIEW"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFERED = "OFFERED"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("recruiter_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(180))
    employment_type: Mapped[str | None] = mapped_column(String(40))
    required_skills: Mapped[list[str]] = mapped_column(
        JSON, default=list, server_default="[]", nullable=False
    )
    minimum_experience_years: Mapped[int | None] = mapped_column(Integer)
    required_education: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    recruiter: Mapped["RecruiterProfile"] = relationship(back_populates="jobs")
    applications: Mapped[list["JobApplication"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    @property
    def company_name(self) -> str | None:
        return self.recruiter.company_name


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=False),
        default=ApplicationStatus.APPLIED,
        nullable=False,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
