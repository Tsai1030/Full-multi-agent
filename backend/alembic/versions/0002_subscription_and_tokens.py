"""subscription plans, user subscriptions, token balances, token transactions, payment records

Revision ID: 0002_subscription_and_tokens
Revises: 0001_initial
Create Date: 2026-06-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_subscription_and_tokens"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users: add subscription_plan column ---
    op.add_column(
        "users",
        sa.Column("subscription_plan", sa.String(20), server_default="free", nullable=False),
    )

    # --- subscription_plans ---
    op.create_table(
        "subscription_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(20), nullable=False),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("price_twd", sa.Integer(), nullable=False),
        sa.Column("monthly_tokens", sa.Integer(), nullable=False),
        sa.Column("max_profiles", sa.Integer(), nullable=False),
        sa.Column("features", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name"),
    )

    # --- seed default plans ---
    op.execute(
        """
        INSERT INTO subscription_plans (id, name, display_name, price_twd, monthly_tokens, max_profiles, features)
        VALUES
            (gen_random_uuid(), 'free',    '免費方案', 0,   5,  2,  '{"career": false, "love": false, "compatibility": false}'::jsonb),
            (gen_random_uuid(), 'basic',   '基本方案', 100, 60, 10, '{"career": true,  "love": false, "compatibility": false}'::jsonb),
            (gen_random_uuid(), 'premium', '高級方案', 300, -1, -1, '{"career": true,  "love": true,  "compatibility": true}'::jsonb)
        """
    )

    # --- user_subscriptions ---
    op.create_table(
        "user_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("payment_provider", sa.String(20), server_default="manual", nullable=False),
        sa.Column("provider_subscription_id", sa.String(255), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancel_at_period_end", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"]),
    )
    op.create_index("ix_user_subscriptions_user_id", "user_subscriptions", ["user_id"], unique=True)

    # --- token_balances ---
    op.create_table(
        "token_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("balance", sa.Integer(), server_default="0", nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_token_balances_user_id", "token_balances", ["user_id"], unique=True)

    # --- token_transactions ---
    op.create_table(
        "token_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("reference_id", sa.String(255), nullable=True),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_token_transactions_user_id", "token_transactions", ["user_id"])

    # --- payment_records ---
    op.create_table(
        "payment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_provider", sa.String(20), nullable=False),
        sa.Column("provider_transaction_id", sa.String(255), nullable=False),
        sa.Column("amount_twd", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("invoice_number", sa.String(100), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["user_subscriptions.id"]),
    )
    op.create_index("ix_payment_records_user_id", "payment_records", ["user_id"])


def downgrade() -> None:
    op.drop_table("payment_records")
    op.drop_table("token_transactions")
    op.drop_table("token_balances")
    op.drop_table("user_subscriptions")
    op.drop_table("subscription_plans")
    op.drop_column("users", "subscription_plan")
