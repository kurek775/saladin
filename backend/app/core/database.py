"""Database engine and session management."""

import logging

from sqlmodel import SQLModel, Session, create_engine

from app.config import settings

logger = logging.getLogger(__name__)

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.DATABASE_URL, echo=False)
    return _engine


def init_db():
    """Create all tables. Safe to call multiple times."""
    engine = get_engine()
    # Import models so SQLModel registers them
    import app.models.database  # noqa: F401
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized")


def get_session() -> Session:
    return Session(get_engine())
