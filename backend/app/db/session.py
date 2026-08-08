"""
Database Session Configuration
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if _IS_SQLITE:
    # SQLite: disable connection pooling (StaticPool issues with threads) and
    # enable WAL mode for better read concurrency.
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA cache_size=-64000")   # 64 MB page cache
        cursor.execute("PRAGMA synchronous=NORMAL")  # faster, still safe with WAL
        cursor.close()

else:
    # PostgreSQL / other RDBMS: use connection pooling.
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,       # verify connections before use
        pool_size=10,             # keep 10 persistent connections
        max_overflow=20,          # allow up to 20 extra connections under load
        pool_recycle=1800,        # recycle connections older than 30 min
        pool_timeout=30,          # wait up to 30 s for a free connection
        echo=settings.DEBUG,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
