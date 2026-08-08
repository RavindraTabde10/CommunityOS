"""
Pytest Configuration and Fixtures
Shared test fixtures and configuration for all tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
from app.models.asset import Asset, AssetBooking, AssetMaintenance
from app.services.auth_service import AuthService


# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user (resident)"""
    password_hash = AuthService.get_password_hash("testpassword123")
    user = User(
        email="testuser@example.com",
        password_hash=password_hash,
        name="Test User",
        phone="1234567890",
        role=UserRole.RESIDENT,
        unit_number="A-101",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db_session):
    """Create a test admin user"""
    password_hash = AuthService.get_password_hash("adminpassword123")
    admin = User(
        email="admin@example.com",
        password_hash=password_hash,
        name="Admin User",
        phone="9876543210",
        role=UserRole.ADMIN,
        unit_number="A-001",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_contractor(db_session):
    """Create a test contractor user"""
    password_hash = AuthService.get_password_hash("contractorpass123")
    contractor = User(
        email="contractor@example.com",
        password_hash=password_hash,
        name="Contractor User",
        phone="5551234567",
        role=UserRole.CONTRACTOR,
        is_active=True
    )
    db_session.add(contractor)
    db_session.commit()
    db_session.refresh(contractor)
    return contractor


@pytest.fixture(scope="function")
def inactive_user(db_session):
    """Create an inactive test user"""
    password_hash = AuthService.get_password_hash("inactivepass123")
    user = User(
        email="inactive@example.com",
        password_hash=password_hash,
        name="Inactive User",
        phone="1112223333",
        role=UserRole.RESIDENT,
        unit_number="B-202",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_token(client, test_admin):
    """Get authentication token for admin user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "adminpassword123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Get authentication headers for test user"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    """Get authentication headers for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def contractor_token(client, test_contractor):
    """Get authentication token for contractor user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_contractor.email,
            "password": "contractorpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def contractor_headers(contractor_token):
    """Get authentication headers for contractor user"""
    return {"Authorization": f"Bearer {contractor_token}"}


@pytest.fixture(scope="function")
def test_issue(db_session, test_user):
    """Create a test issue"""
    issue = Issue(
        id="RGTS-000001",
        issue_number="000001",
        title="Test Issue",
        description="This is a test issue",
        category=IssueCategory.ELECTRICAL,
        priority=IssuePriority.MEDIUM,
        status=IssueStatus.OPEN,
        location="Building A, Floor 1",
        unit_number="A-101",
        reported_by=test_user.id
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue
