from sqlalchemy import (
    create_engine,
)

from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from database.config import (
    DATABASE_URL,
)


# ======================================================
# ENGINE
# ======================================================

engine = create_engine(
    DATABASE_URL,

    echo=False,

    pool_pre_ping=True,
)


# ======================================================
# SESSION FACTORY
# ======================================================

SessionLocal = sessionmaker(
    bind=engine,

    autoflush=False,

    autocommit=False,
)


# ======================================================
# FASTAPI DEPENDENCY
# ======================================================

def get_db():

    db: Session = SessionLocal()

    try:

        yield db

    finally:

        db.close()