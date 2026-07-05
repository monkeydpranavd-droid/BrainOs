from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Verify the connection before handing it back from the pool.
    pool_pre_ping=True,
    # Recycle connections every 10 minutes to avoid stale connections
    # being closed by Supabase's idle timeout.
    pool_recycle=600,
    # Keep a small pool; Supabase free tier has a 60-connection limit.
    pool_size=5,
    max_overflow=10,
    # Log SQL in development; set to False in production.
    echo=(settings.APP_ENV == "development"),
    # psycopg2 connect_args: enforce SSL for Supabase.
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)