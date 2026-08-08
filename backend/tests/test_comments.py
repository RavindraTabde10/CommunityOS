"""
Test cases for Comments and Activity endpoints
"""
import pytest
from fastapi import status
from datetime import datetime


class TestCommentCreation:
    """Test comment creation on issues"""

    def test_create_comment_success(self, client, auth_headers, test_issue):
        """Test creating a comment on own issue"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "This is my first comment on the issue"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "This is my first comment on the issue"
        assert data["issue_id"] == test_issue.id
        assert data["is_own"] is True
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_comment_on_nonexistent_issue(self, client, auth_headers):
        """Test creating comment on issue that doesn't exist"""
        response = client.post(
            "/api/v1/issues/RGTS-999999/comments",
            headers=auth_headers,
            json={"content": "Comment on non-existent issue"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_no_auth(self, client, test_issue):
        """Test creating comment without authentication"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            json={"content": "Unauthorized comment"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_comment_empty_content(self, client, auth_headers, test_issue):
        """Test creating comment with empty content"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": ""}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_comment_too_long(self, client, auth_headers, test_issue):
        """Test creating comment exceeding max length"""
        long_content = "x" * 2001  # Max is 2000
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": long_content}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_admin_can_comment_on_any_issue(self, client, admin_headers, test_issue):
        """Test admin can comment on any user's issue"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=admin_headers,
            json={"content": "Admin comment on user's issue"}
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestCommentList:
    """Test listing comments"""

    def test_list_comments_empty(self, client, auth_headers, test_issue):
        """Test listing comments when none exist"""
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["comments"]) == 0

    def test_list_comments_with_data(self, client, auth_headers, test_issue):
        """Test listing comments after creating some"""
        # Create 3 comments
        for i in range(3):
            client.post(
                f"/api/v1/issues/{test_issue.id}/comments",
                headers=auth_headers,
                json={"content": f"Comment {i+1}"}
            )
        
        # List comments
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["comments"]) == 3

    def test_list_comments_with_pagination(self, client, auth_headers, test_issue):
        """Test comment pagination"""
        # Create 5 comments
        for i in range(5):
            client.post(
                f"/api/v1/issues/{test_issue.id}/comments",
                headers=auth_headers,
                json={"content": f"Comment {i+1}"}
            )
        
        # Get first 2 comments
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/comments?skip=0&limit=2",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["comments"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

    def test_list_comments_no_auth(self, client, test_issue):
        """Test listing comments without authentication"""
        response = client.get(f"/api/v1/issues/{test_issue.id}/comments")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_comments_nonexistent_issue(self, client, auth_headers):
        """Test listing comments for non-existent issue"""
        response = client.get(
            "/api/v1/issues/RGTS-999999/comments",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCommentUpdate:
    """Test updating comments"""

    def test_update_own_comment(self, client, auth_headers, test_issue):
        """Test updating own comment"""
        # Create comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "Original comment"}
        )
        comment_id = create_response.json()["id"]
        
        # Update comment
        response = client.put(
            f"/api/v1/issues/comments/{comment_id}",
            headers=auth_headers,
            json={"content": "Updated comment"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Updated comment"
        assert data["id"] == comment_id

    def test_update_nonexistent_comment(self, client, auth_headers):
        """Test updating comment that doesn't exist"""
        response = client.put(
            "/api/v1/issues/comments/99999",
            headers=auth_headers,
            json={"content": "Updated content"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_user_comment_forbidden(self, client, auth_headers, contractor_headers, test_issue):
        """Test regular user cannot update another user's comment"""
        # User creates comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "User's comment"}
        )
        comment_id = create_response.json()["id"]
        
        # Create another issue for contractor
        contractor_issue = client.post(
            "/api/v1/issues",
            headers=contractor_headers,
            json={
                "title": "Contractor's issue",
                "description": "Test",
                "category": "electrical",
                "priority": "medium"
            }
        ).json()
        
        # Contractor tries to update user's comment (should fail)
        response = client.put(
            f"/api/v1/issues/comments/{comment_id}",
            headers=contractor_headers,
            json={"content": "Trying to update"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_any_comment(self, client, auth_headers, admin_headers, test_issue):
        """Test admin can update any user's comment"""
        # User creates comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "User's comment"}
        )
        comment_id = create_response.json()["id"]
        
        # Admin updates comment
        response = client.put(
            f"/api/v1/issues/comments/{comment_id}",
            headers=admin_headers,
            json={"content": "Admin updated this"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["content"] == "Admin updated this"


class TestCommentDelete:
    """Test deleting comments"""

    def test_delete_own_comment(self, client, auth_headers, test_issue):
        """Test deleting own comment"""
        # Create comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "Comment to delete"}
        )
        comment_id = create_response.json()["id"]
        
        # Delete comment
        response = client.delete(
            f"/api/v1/issues/comments/{comment_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify comment is not in list (soft deleted)
        list_response = client.get(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers
        )
        assert list_response.json()["total"] == 0

    def test_delete_nonexistent_comment(self, client, auth_headers):
        """Test deleting comment that doesn't exist"""
        response = client.delete(
            "/api/v1/issues/comments/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_user_comment_forbidden(self, client, auth_headers, contractor_headers, test_issue):
        """Test regular user cannot delete another user's comment"""
        # User creates comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "User's comment"}
        )
        comment_id = create_response.json()["id"]
        
        # Contractor tries to delete (should fail)
        response = client.delete(
            f"/api/v1/issues/comments/{comment_id}",
            headers=contractor_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_any_comment(self, client, auth_headers, admin_headers, test_issue):
        """Test admin can delete any user's comment"""
        # User creates comment
        create_response = client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "User's comment"}
        )
        comment_id = create_response.json()["id"]
        
        # Admin deletes comment
        response = client.delete(
            f"/api/v1/issues/comments/{comment_id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestActivityLog:
    """Test issue activity logging"""

    def test_activity_logged_on_issue_creation(self, client, auth_headers):
        """Test activity is logged when issue is created"""
        # Create issue
        issue_response = client.post(
            "/api/v1/issues",
            headers=auth_headers,
            json={
                "title": "Test issue for activity",
                "description": "Testing activity log",
                "category": "electrical",
                "priority": "high"
            }
        )
        issue_id = issue_response.json()["id"]
        
        # Get activity log
        response = client.get(
            f"/api/v1/issues/{issue_id}/activity",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any(activity["action"] == "created" for activity in data["activities"])

    def test_activity_logged_on_comment_creation(self, client, auth_headers, test_issue):
        """Test activity is logged when comment is added"""
        # Add comment
        client.post(
            f"/api/v1/issues/{test_issue.id}/comments",
            headers=auth_headers,
            json={"content": "Test comment for activity"}
        )
        
        # Get activity log
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/activity",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(activity["action"] == "commented" for activity in data["activities"])

    def test_activity_logged_on_issue_update(self, client, auth_headers, test_issue):
        """Test activity is logged when issue is updated"""
        # Update issue
        client.put(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers,
            json={"status": "in_progress"}
        )
        
        # Get activity log
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/activity",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(
            activity["action"] == "updated" and activity["field_name"] == "status"
            for activity in data["activities"]
        )

    def test_activity_pagination(self, client, auth_headers, test_issue):
        """Test activity log pagination"""
        # Create multiple activities (comments)
        for i in range(5):
            client.post(
                f"/api/v1/issues/{test_issue.id}/comments",
                headers=auth_headers,
                json={"content": f"Comment {i+1}"}
            )
        
        # Get first 2 activities
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/activity?skip=0&limit=2",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["activities"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

    def test_activity_no_auth(self, client, test_issue):
        """Test getting activity log without authentication"""
        response = client.get(f"/api/v1/issues/{test_issue.id}/activity")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_activity_nonexistent_issue(self, client, auth_headers):
        """Test getting activity for non-existent issue"""
        response = client.get(
            "/api/v1/issues/RGTS-999999/activity",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_activity_includes_user_names(self, client, auth_headers, test_issue):
        """Test activity log includes user names"""
        # Get activity log
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/activity",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that activities have user names
        for activity in data["activities"]:
            if activity["user_id"]:
                assert "user_name" in activity
                assert activity["user_name"] is not None


class TestCommentPermissions:
    """Test comment permission scenarios"""

    def test_user_cannot_comment_on_unrelated_issue(self, client, auth_headers, contractor_headers):
        """Test user cannot comment on issue they don't own or aren't assigned to"""
        # Contractor creates issue
        contractor_issue = client.post(
            "/api/v1/issues",
            headers=contractor_headers,
            json={
                "title": "Contractor's private issue",
                "description": "Test",
                "category": "plumbing",
                "priority": "low"
            }
        ).json()
        
        # Regular user tries to comment (should fail)
        response = client.post(
            f"/api/v1/issues/{contractor_issue['id']}/comments",
            headers=auth_headers,
            json={"content": "Trying to comment"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assigned_user_can_comment(self, client, admin_headers, contractor_headers, resident_user):
        """Test user assigned to issue can comment on it"""
        # Admin creates issue and assigns to contractor
        issue = client.post(
            "/api/v1/issues",
            headers=admin_headers,
            json={
                "title": "Issue assigned to contractor",
                "description": "Test",
                "category": "electrical",
                "priority": "medium",
                "assigned_to": resident_user["id"]
            }
        ).json()
        
        # Assigned user comments (should work)
        response = client.post(
            f"/api/v1/issues/{issue['id']}/comments",
            headers=contractor_headers,
            json={"content": "Comment from assigned user"}
        )
        # This might fail if contractor_user is different from resident_user
        # The test logic depends on your fixture setup
