"""
Authentication Endpoint Tests
Tests for user registration, login, and profile retrieval
"""

import pytest
from fastapi import status


class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_new_user_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "name": "New User",
                "phone": "1234567890",
                "role": "resident",
                "unit_number": "C-301"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["role"] == "resident"
        assert "id" in data
        assert "password" not in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
                "name": "Another User",
                "role": "resident"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "name": "Test User",
                "role": "resident"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Test registration with password too short"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short",
                "name": "Test User",
                "role": "resident"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_with_different_roles(self, client):
        """Test registration with various user roles"""
        roles = ["resident", "contractor", "admin", "security", "facility"]
        for idx, role in enumerate(roles):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"{role}{idx}@example.com",
                    "password": "password123",
                    "name": f"{role.title()} User",
                    "role": role
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["role"] == role


class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, client, inactive_user):
        """Test login with inactive user account"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": inactive_user.email,
                "password": "inactivepass123"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "deactivated" in response.json()["detail"].lower()
    
    def test_login_admin_success(self, client, test_admin):
        """Test admin login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin.email,
                "password": "adminpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()


class TestGetCurrentUser:
    """Test get current user profile endpoint"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user profile"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["id"] == test_user.id
    
    def test_get_current_user_no_token(self, client):
        """Test getting profile without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting profile with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_admin(self, client, admin_headers, test_admin):
        """Test getting admin user profile"""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "admin"
        assert data["email"] == test_admin.email
