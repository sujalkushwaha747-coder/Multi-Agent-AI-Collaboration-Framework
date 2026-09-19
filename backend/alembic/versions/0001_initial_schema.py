"""Initial ShodhAI schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_extension", sa.String(length=16), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_documents_status", "documents", ["status"])

    op.create_table(
        "benchmark_prompts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_benchmark_prompts_category", "benchmark_prompts", ["category"])

    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=120), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "experiments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("task_category", sa.String(length=40), nullable=False),
        sa.Column("reference_answer", sa.Text(), nullable=True),
        sa.Column("document_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_experiments_task_category", "experiments", ["task_category"])
    op.create_index("ix_experiments_status", "experiments", ["status"])

    op.create_table(
        "single_agent_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("experiment_id", sa.String(length=36), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("execution_time_seconds", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("retrieval_context", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("experiment_id"),
    )
    op.create_index("ix_single_agent_results_experiment_id", "single_agent_results", ["experiment_id"])

    op.create_table(
        "multi_agent_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("experiment_id", sa.String(length=36), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("execution_time_seconds", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("revision_attempts", sa.Integer(), nullable=False),
        sa.Column("retrieval_context", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("experiment_id"),
    )
    op.create_index("ix_multi_agent_results_experiment_id", "multi_agent_results", ["experiment_id"])

    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("experiment_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("accuracy_single", sa.Float(), nullable=True),
        sa.Column("accuracy_multi", sa.Float(), nullable=True),
        sa.Column("quality_single", sa.Float(), nullable=True),
        sa.Column("quality_multi", sa.Float(), nullable=True),
        sa.Column("hallucination_single", sa.Float(), nullable=True),
        sa.Column("hallucination_multi", sa.Float(), nullable=True),
        sa.Column("completeness_single", sa.Float(), nullable=True),
        sa.Column("completeness_multi", sa.Float(), nullable=True),
        sa.Column("overall_single", sa.Float(), nullable=True),
        sa.Column("overall_multi", sa.Float(), nullable=True),
        sa.Column("winner", sa.String(length=40), nullable=True),
        sa.Column("methodology", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("experiment_id"),
    )
    op.create_index("ix_evaluation_results_experiment_id", "evaluation_results", ["experiment_id"])

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("experiment_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=80), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("output", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_agent_runs_agent_name", "agent_runs", ["agent_name"])
    op.create_index("ix_agent_runs_experiment_id", "agent_runs", ["experiment_id"])


def downgrade() -> None:
    op.drop_index("ix_agent_runs_experiment_id", table_name="agent_runs")
    op.drop_index("ix_agent_runs_agent_name", table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index("ix_evaluation_results_experiment_id", table_name="evaluation_results")
    op.drop_table("evaluation_results")
    op.drop_index("ix_multi_agent_results_experiment_id", table_name="multi_agent_results")
    op.drop_table("multi_agent_results")
    op.drop_index("ix_single_agent_results_experiment_id", table_name="single_agent_results")
    op.drop_table("single_agent_results")
    op.drop_index("ix_experiments_status", table_name="experiments")
    op.drop_index("ix_experiments_task_category", table_name="experiments")
    op.drop_table("experiments")
    op.drop_table("system_settings")
    op.drop_index("ix_benchmark_prompts_category", table_name="benchmark_prompts")
    op.drop_table("benchmark_prompts")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

