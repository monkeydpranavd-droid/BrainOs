"""
alembic/env.py
─────────────────────────────────────────────────────────────────────────────
Alembic migration environment.

Configured to:
  - Import all SQLAlchemy models so autogenerate detects them
  - Read DATABASE_URL from BrainOS settings (not alembic.ini)
  - Support async (via run_migrations_online with a sync engine)
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# ── Make app importable from here ─────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.db.base import Base  # noqa: F401 — needed for metadata

# Import ALL models here so Alembic autogenerate detects them.
# Add new models to this list as the project grows.
from app.models.user import User  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.organization_member import OrganizationMember  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401
from app.models.workspace_member import WorkspaceMember  # noqa: F401
from app.models.invitation import Invitation  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.knowledge_base import KnowledgeBase  # noqa: F401
from app.models.folder import Folder  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_version import DocumentVersion  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.document_tag import DocumentTag  # noqa: F401

# ── Alembic config ────────────────────────────────────────────────────────────

config = context.config

# Override sqlalchemy.url from alembic.ini with our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(obj, name, type_, reflected, compare_to):
    """
    Only include objects in the 'public' schema.
    This prevents Alembic from detecting Supabase's internal schemas
    (auth, storage, realtime, vault) as foreign tables to drop.
    """
    if type_ == "table":
        schema = getattr(obj, "schema", None)
        return schema == "public" or schema is None
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script output)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table_schema="public",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (direct DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"sslmode": "require"},
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            version_table_schema="public",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
