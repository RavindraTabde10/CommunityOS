"""
User Management Endpoint Tests
Tests for user profile updates, password changes, and admin user management
"""

import pytest
from fastapi import status


class TestUserProfile:
    """Test user profile management endpoints"""
    
    def test_update_own_profile_success(self, client, auth_headers, test_user):
        """Test updating own profile"""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "phone": "9999999999",
                "unit_number": "B-202"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["phone"] == "9999999999"
        assert data["unit_number"] == "B-202"
    
    def test_update_profile_partial(self, client, auth_headers):
        """Test partial profile update"""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"name": "Only Name Updated"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Only Name Updated"
    
    def test_update_profile_no_auth(self, client):
        """Test updating profile without authentication"""
        response = client.put(
            "/api/v1/users/me",
            json={"name": "Should Fail"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPasswordChange:
    """Test password change endpoint"""
    
    def test_change_password_success(self, client, auth_headers):
        """Test successful password change"""
        response = client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newtestpassword456"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password"""
        response = client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_change_password_same_as_current(self, client, auth_headers):
        """Test password change with same password"""
        response = client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "different" in response.json()["detail"].lower()
    
    def test_change_password_too_short(self, client, auth_headers):
        """Test password change with short password"""
        response = client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "short"
            }
        )
        # Pydantic validation returns 422 for schema validation errors
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPasswordReset:
    """Test password reset flow"""
    
    def test_forgot_password_existing_user(self, client, test_user):
        """Test password reset request for existing user"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reset_token" in data  # Development only
    
    def test_forgot_password_nonexistent_user(self, client):
        """Test password reset request for non-existent user"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        # Should return 200 to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
    
    def test_reset_password_with_token(self, client, test_user):
        """Test resetting password with valid token"""
        # First, get reset token
        forgot_response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )
        reset_token = forgot_response.json()["reset_token"]
        
        # Now reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "brandnewpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()
    
    def test_reset_password_invalid_token(self, client):
        """Test resetting password with invalid token"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAdminUserManagement:
    """Test admin user management endpoints"""
    
    def test_list_users_as_admin(self, client, admin_headers, test_user):
        """Test listing all users as admin"""
        response = client.get("/api/v1/users", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 1
    
    def test_list_users_as_regular_user(self, client, auth_headers):
        """Test listing users as regular user (should fail)"""
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_users_with_pagination(self, client, admin_headers):
        """Test user listing with pagination"""
        response = client.get(
            "/api/v1/users?skip=0&limit=5",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["users"]) <= 5
    
    def test_list_users_with_role_filter(self, client, admin_headers):
        """Test user listing filtered by role"""
        response = client.get(
            "/api/v1/users?role=admin",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data["users"]:
            assert user["role"] == "admin"
    
    def test_list_users_with_search(self, client, admin_headers, test_user):
        """Test user listing with search"""
        response = client.get(
            f"/api/v1/users?search={test_user.name}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
    
    def test_update_other_user_as_admin(self, client, admin_headers, test_user):
        """Test admin updating another user's profile"""
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            headers=admin_headers,
            json={
                "name": "Admin Updated Name",
                "unit_number": "Z-999"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Admin Updated Name"
        assert data["unit_number"] == "Z-999"
    
    def test_update_other_user_as_regular_user(self, client, auth_headers, test_admin):
        """Test regular user updating another user (should fail)"""
        response = client.put(
            f"/api/v1/users/{test_admin.id}",
            headers=auth_headers,
            json={"name": "Should Fail"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_user_role_as_admin(self, client, admin_headers, test_user):
        """Test admin changing user role"""
        response = client.patch(
            f"/api/v1/users/{test_user.id}/role",
            headers=admin_headers,
            json={"role": "contractor"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "contractor"
    
    def test_admin_cannot_change_own_role(self, client, admin_headers, test_admin):
        """Test admin cannot change their own role"""
        response = client.patch(
            f"/api/v1/users/{test_admin.id}/role",
            headers=admin_headers,
            json={"role": "resident"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_deactivate_user_as_admin(self, client, admin_headers, test_user):
        """Test admin deactivating a user"""
        response = client.patch(
            f"/api/v1/users/{test_user.id}/status",
            headers=admin_headers,
            json={"is_active": False}
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_admin_cannot_deactivate_self(self, client, admin_headers, test_admin):
        """Test admin cannot deactivate themselves"""
        response = client.patch(
            f"/api/v1/users/{test_admin.id}/status",
            headers=admin_headers,
            json={"is_active": False}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_user_as_admin(self, client, admin_headers, test_contractor):
        """Test admin deleting a user"""
        response = client.delete(
            f"/api/v1/users/{test_contractor.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deleted
        get_response = client.get("/api/v1/users", headers=admin_headers)
        users = get_response.json()["users"]
        user_ids = [u["id"] for u in users]
        assert test_contractor.id not in user_ids
    
    def test_admin_cannot_delete_self(self, client, admin_headers, test_admin):
        """Test admin cannot delete themselves"""
        response = client.delete(
            f"/api/v1/users/{test_admin.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
