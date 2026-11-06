
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from config import settings
from database import get_db, Base
from oauth2 import create_access_token

# IMPORTANT: Use the same import style everywhere.
import models


# Test database URL
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Create a fresh database session for each test
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


# Create test client
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


# Create first test user
@pytest.fixture()
def test_user(client):
    user_data = {
        "email": "raksha@email.com",
        "password": "rak12"
    }

    response = client.post("/users", json=user_data)

    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = user_data["password"]

    return new_user


# Create second test user
@pytest.fixture()
def test_user2(client):
    user_data = {
        "email": "raksha2@email.com",
        "password": "rak12"
    }

    response = client.post("/users", json=user_data)

    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = user_data["password"]

    return new_user


# Generate authentication token
@pytest.fixture()
def token(test_user):
    return create_access_token({
        "user_id": test_user["id"]
    })


# Create authenticated test client
@pytest.fixture()
def authorized_client(client, token):
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client


# Create sample posts for testing
@pytest.fixture()
def test_posts(test_user, session, test_user2):

    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user["id"]
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user["id"]
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user["id"]
        },
        {
            "title": "4th title",
            "content": "4th content",
            "owner_id": test_user2["id"]
        }
    ]

    posts = [
        models.Post(**post)
        for post in posts_data
    ]

    session.add_all(posts)
    session.commit()

    return session.query(models.Post).all()
