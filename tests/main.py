import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base

engine_test = create_engine("sqlite:///./data/test.db",
                            connect_args={"check_same_thread": False})
SessionLocalTest = sessionmaker(autocommit=False,
                                autoflush=False, bind=engine_test)


def override_get_db():
    db = None
    try:
        db = SessionLocalTest()
        yield db
    finally:
        if db is not None:
            db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
