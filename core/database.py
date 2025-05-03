from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

db_dir = settings.database_path
db_dir.mkdir(parents=True, exist_ok=True)

db_path = db_dir / "weather.db"
database_url = f"sqlite:///{db_path}"

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Generator for yielding our database so that
     it can be used in dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
