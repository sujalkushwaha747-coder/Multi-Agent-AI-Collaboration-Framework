from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    task_category: Mapped[str] = mapped_column(String(40), index=True, default="general")
    reference_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="created", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    single_result: Mapped["SingleAgentResult | None"] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        uselist=False,
    )
    multi_result: Mapped["MultiAgentResult | None"] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        uselist=False,
    )
    evaluation: Mapped["EvaluationResult | None"] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        uselist=False,
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        order_by="AgentRun.sequence",
    )


class SingleAgentResult(Base):
    __tablename__ = "single_agent_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), unique=True, index=True
    )
    response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="completed")
    execution_time_seconds: Mapped[float | None] = mapped_column(Float)
    model_name: Mapped[str | None] = mapped_column(String(120))
    retrieval_context: Mapped[list[dict]] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    experiment: Mapped[Experiment] = relationship(back_populates="single_result")


class MultiAgentResult(Base):
    __tablename__ = "multi_agent_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), unique=True, index=True
    )
    response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="completed")
    execution_time_seconds: Mapped[float | None] = mapped_column(Float)
    model_name: Mapped[str | None] = mapped_column(String(120))
    revision_attempts: Mapped[int] = mapped_column(Integer, default=0)
    retrieval_context: Mapped[list[dict]] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    experiment: Mapped[Experiment] = relationship(back_populates="multi_result")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), unique=True, index=True
    )
    status: Mapped[str] = mapped_column(String(40), default="completed")
    accuracy_single: Mapped[float | None] = mapped_column(Float)
    accuracy_multi: Mapped[float | None] = mapped_column(Float)
    quality_single: Mapped[float | None] = mapped_column(Float)
    quality_multi: Mapped[float | None] = mapped_column(Float)
    hallucination_single: Mapped[float | None] = mapped_column(Float)
    hallucination_multi: Mapped[float | None] = mapped_column(Float)
    completeness_single: Mapped[float | None] = mapped_column(Float)
    completeness_multi: Mapped[float | None] = mapped_column(Float)
    overall_single: Mapped[float | None] = mapped_column(Float)
    overall_multi: Mapped[float | None] = mapped_column(Float)
    winner: Mapped[str | None] = mapped_column(String(40), nullable=True)
    methodology: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[list[dict]] = mapped_column(JSON, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    experiment: Mapped[Experiment] = relationship(back_populates="evaluation")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), index=True
    )
    agent_name: Mapped[str] = mapped_column(String(80), index=True)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    experiment: Mapped[Experiment] = relationship(back_populates="agent_runs")

