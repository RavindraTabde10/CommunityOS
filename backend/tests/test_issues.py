"""
Issue Management Endpoint Tests
Tests for issue CRUD operations
"""

import pytest
from fastapi import status


class TestCreateIssue:
    """Test issue creation endpoint"""
    
    def test_create_issue_success(self, client, auth_headers, test_user):
        """Test successful issue creation"""
        response = client.post(
            "/api/v1/issues/",
            headers=auth_headers,
            json={
                "title": "Broken Light",
                "description": "Light in living room is not working",
                "category": "electrical",
                "priority": "high",
                "location": "Building A, Floor 3",
                "unit_number": "A-301"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Broken Light"
        assert data["category"] == "electrical"
        assert data["status"] == "open"
        assert "RGTS-" in data["id"]
        assert data["reporter"]["id"] == test_user.id
    
    def test_create_issue_minimal_fields(self, client, auth_headers):
        """Test creating issue with minimal required fields"""
        response = client.post(
            "/api/v1/issues/",
            headers=auth_headers,
            json={
                "title": "Simple Issue",
                "category": "other"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["priority"] == "medium"  # Default priority
    
    def test_create_issue_invalid_category(self, client, auth_headers):
        """Test creating issue with invalid category"""
        response = client.post(
            "/api/v1/issues/",
            headers=auth_headers,
            json={
                "title": "Test Issue",
                "category": "invalid_category"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_issue_invalid_priority(self, client, auth_headers):
        """Test creating issue with invalid priority"""
        response = client.post(
            "/api/v1/issues/",
            headers=auth_headers,
            json={
                "title": "Test Issue",
                "category": "electrical",
                "priority": "invalid_priority"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_issue_no_auth(self, client):
        """Test creating issue without authentication"""
        response = client.post(
            "/api/v1/issues/",
            json={
                "title": "Test Issue",
                "category": "electrical"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_multiple_issues(self, client, auth_headers):
        """Test creating multiple issues generates unique IDs"""
        ids = []
        for i in range(3):
            response = client.post(
                "/api/v1/issues/",
                headers=auth_headers,
                json={
                    "title": f"Issue {i}",
                    "category": "electrical"
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            ids.append(response.json()["id"])
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))


class TestListIssues:
    """Test issue listing endpoint"""
    
    def test_list_issues_as_user(self, client, auth_headers, test_issue, test_user):
        """Test user sees only their own issues"""
        response = client.get("/api/v1/issues/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # User should only see their own issues
        for issue in data:
            assert issue["reporter"]["id"] == test_user.id
    
    def test_list_issues_as_admin(self, client, admin_headers, test_issue):
        """Test admin sees all issues"""
        response = client.get("/api/v1/issues/", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_issues_with_status_filter(self, client, admin_headers, test_issue):
        """Test filtering issues by status"""
        response = client.get(
            "/api/v1/issues/?status=open",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for issue in data:
            assert issue["status"] == "open"
    
    def test_list_issues_with_category_filter(self, client, admin_headers, test_issue):
        """Test filtering issues by category"""
        response = client.get(
            "/api/v1/issues/?category=electrical",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for issue in data:
            assert issue["category"] == "electrical"
    
    def test_list_issues_with_pagination(self, client, admin_headers):
        """Test issue pagination"""
        # Create multiple issues first
        response = client.get(
            "/api/v1/issues/?skip=0&limit=2",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    def test_list_issues_no_auth(self, client):
        """Test listing issues without authentication"""
        response = client.get("/api/v1/issues/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetIssue:
    """Test get single issue endpoint"""
    
    def test_get_issue_success(self, client, auth_headers, test_issue):
        """Test getting issue details"""
        response = client.get(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_issue.id
        assert data["title"] == test_issue.title
    
    def test_get_issue_not_found(self, client, auth_headers):
        """Test getting non-existent issue"""
        response = client.get(
            "/api/v1/issues/RGTS-999999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_other_user_issue_as_regular_user(self, client, auth_headers, db_session, test_admin):
        """Test regular user cannot see other user's issue"""
        from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
        
        # Create issue for admin
        admin_issue = Issue(
            id="RGTS-999999",
            issue_number="999999",
            title="Admin Issue",
            category=IssueCategory.PLUMBING,
            priority=IssuePriority.LOW,
            status=IssueStatus.OPEN,
            reported_by=test_admin.id
        )
        db_session.add(admin_issue)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/issues/{admin_issue.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_any_issue_as_admin(self, client, admin_headers, test_issue):
        """Test admin can see any issue"""
        response = client.get(
            f"/api/v1/issues/{test_issue.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestUpdateIssue:
    """Test issue update endpoint"""
    
    def test_update_own_issue(self, client, auth_headers, test_issue):
        """Test updating own issue"""
        response = client.put(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "priority": "critical",
                "status": "in_progress"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "critical"
        assert data["status"] == "in_progress"
    
    def test_update_issue_partial(self, client, auth_headers, test_issue):
        """Test partial issue update"""
        response = client.put(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers,
            json={"status": "resolved"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "resolved"
    
    def test_update_other_user_issue(self, client, auth_headers, db_session, test_admin):
        """Test regular user cannot update other user's issue"""
        from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
        
        admin_issue = Issue(
            id="RGTS-888888",
            issue_number="888888",
            title="Admin Issue",
            category=IssueCategory.PAINTING,
            priority=IssuePriority.LOW,
            status=IssueStatus.OPEN,
            reported_by=test_admin.id
        )
        db_session.add(admin_issue)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/issues/{admin_issue.id}",
            headers=auth_headers,
            json={"title": "Should Fail"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_any_issue_as_admin(self, client, admin_headers, test_issue):
        """Test admin can update any issue"""
        response = client.put(
            f"/api/v1/issues/{test_issue.id}",
            headers=admin_headers,
            json={"status": "closed"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "closed"
    
    def test_update_nonexistent_issue(self, client, auth_headers):
        """Test updating non-existent issue"""
        response = client.put(
            "/api/v1/issues/RGTS-999999",
            headers=auth_headers,
            json={"title": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteIssue:
    """Test issue deletion endpoint"""
    
    def test_delete_own_issue(self, client, auth_headers, test_issue):
        """Test deleting own issue"""
        response = client.delete(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify issue is deleted
        get_response = client.get(
            f"/api/v1/issues/{test_issue.id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_other_user_issue(self, client, auth_headers, db_session, test_admin):
        """Test regular user cannot delete other user's issue"""
        from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
        
        admin_issue = Issue(
            id="RGTS-777777",
            issue_number="777777",
            title="Admin Issue to Delete",
            category=IssueCategory.CIVIL,
            priority=IssuePriority.LOW,
            status=IssueStatus.OPEN,
            reported_by=test_admin.id
        )
        db_session.add(admin_issue)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/issues/{admin_issue.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_any_issue_as_admin(self, client, admin_headers, test_issue):
        """Test admin can delete any issue"""
        response = client.delete(
            f"/api/v1/issues/{test_issue.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_nonexistent_issue(self, client, auth_headers):
        """Test deleting non-existent issue"""
        response = client.delete(
            "/api/v1/issues/RGTS-999999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
