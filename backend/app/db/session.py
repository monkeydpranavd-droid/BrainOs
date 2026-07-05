from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Recycle connections every 10 minutes to avoid stale connections
    # being closed by Supabase's idle timeout (default 600s).
    pool_recycle=300,
    # pre_ping adds ~80ms round-trip overhead on EVERY connection checkout
    # from the pool. Disabled in favour of pool_recycle to handle stale conns.
    pool_pre_ping=False,
    # Increase pool size: 3 frontend routes (me + orgs + workspaces) + workers
    pool_size=10,
    max_overflow=20,
    # Log SQL in development; set to False in production.
    echo=(settings.APP_ENV == "development"),
    # psycopg2 connect_args: enforce SSL for Supabase.
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        # keepalives prevent idle connection drops by the cloud proxy
        "keepalives": 1,
        "keepalives_idle": 60,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)