"""create_users_table

Revision ID: 0bc741a5a65c
Revises:
Create Date: 2026-07-05

Creates the public.users table for BrainOS local user profiles.
Supabase auth.users is managed by Supabase — we only own public.users.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0bc741a5a65c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "supabase_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="References auth.users.id in Supabase. Never store credentials here.",
        ),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=256), nullable=True),
        sa.Column("avatar_url", sa.String(length=2048), nullable=True),
        sa.Column(
            "role",
            sa.String(length=32),
            server_default="member",
            nullable=False,
            comment="One of: owner, admin, member, viewer",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("supabase_user_id", name="uq_users_supabase_user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        schema="public",
    )

    op.create_index(
        "ix_users_supabase_user_id",
        "users",
        ["supabase_user_id"],
        unique=False,
        schema="public",
    )
    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=False,
        schema="public",
    )
    op.create_index(
        "ix_users_is_active",
        "users",
        ["is_active"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    op.drop_index("ix_users_is_active", table_name="users", schema="public")
    op.drop_index("ix_users_email", table_name="users", schema="public")
    op.drop_index("ix_users_supabase_user_id", table_name="users", schema="public")
    op.drop_table("users", schema="public")
