import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
import main as app_module

engine = create_engine(
    'sqlite://',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app_module.app.dependency_overrides[get_db] = override_get_db
    with TestClient(app_module.app) as c:
        yield c
    app_module.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
