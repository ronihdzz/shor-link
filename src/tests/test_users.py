import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from utils import get_db
from main import app
import unittest

DATABASE_NAME = os.getenv("DATABASE_NAME", "test_users.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        db_file = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_file):
            os.remove(db_file)

    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = self.override_get_db
        self.setup_database()

    def tearDown(self):
        app.dependency_overrides[get_db] = get_db
        self.teardown_database()

    @staticmethod
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def setup_database(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def teardown_database(self):
        Base.metadata.drop_all(bind=engine)

    def test_create_user(self):
        response = self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "testuser@example.com")
        self.assertIn("id", data)

    def test_create_user_duplicate_username(self):
        self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser1@example.com", "password": "password123"})
        response = self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser2@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Username already registered", response.json()["detail"])

    def test_create_user_duplicate_email(self):
        self.client.post("/v1/users/", json={"username": "testuser1", "email": "testuser@example.com", "password": "password123"})
        response = self.client.post("/v1/users/", json={"username": "testuser2", "email": "testuser@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email already registered", response.json()["detail"])

    def test_login_user(self):
        self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
        response = self.client.post("/v1/token", data={"username": "testuser", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_login_user_invalid_credentials(self):
        self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
        response = self.client.post("/v1/token", data={"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Incorrect username or password", response.json()["detail"])

    def test_get_current_user(self):
        self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
        token_response = self.client.post("/v1/token", data={"username": "testuser", "password": "password123"})
        token = token_response.json()["access_token"]
        response = self.client.get("/v1/users/me/", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "testuser@example.com")

    def test_delete_user(self):
        self.client.post("/v1/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
        token_response = self.client.post("/v1/token", data={"username": "testuser", "password": "password123"})
        token = token_response.json()["access_token"]
        response = self.client.delete("/v1/users/me/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "User deleted" in response.json()["detail"]
        get_response = self.client.get("/v1/users/me/", headers={"Authorization": f"Bearer {token}"})
        assert get_response.status_code == 401
        assert "User not found or deleted" in get_response.json()["detail"]
