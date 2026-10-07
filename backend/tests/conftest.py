"""
conftest.py - Pytest configuration for the test suite.
Configures an in-memory SQLite database for all tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# ─── 1. Patch the database BEFORE any app imports ─────────────────────────────
# SQLite in-memory databases are per-connection by default.
# StaticPool forces all connections to reuse the same underlying connection,
# so tables created in setup are visible to request-handling threads.
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

import app.database as db_module
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal

# ─── 2. Now import the app ────────────────────────────────────────────────────
from app.main import app
from app.database import get_db, Base


# ─── 3. Override the DB dependency ────────────────────────────────────────────
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ─── 4. Create/drop tables around each test ────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_db():
    """Create all tables before each test and drop them after."""
    from app.models import form, question, response  # noqa: F401
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(reset_db):
    """Test client. reset_db ensures tables exist before any request."""
    with TestClient(app) as c:
        yield c

