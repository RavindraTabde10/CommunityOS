"""
Photo Upload Endpoint Tests
Tests for issue photo upload, listing, and deletion
"""

import pytest
from fastapi import status
from io import BytesIO


class TestPhotoUpload:
    """Test photo upload endpoint"""
    
    @pytest.fixture
    def mock_image_file(self):
        """Create a mock image file for testing"""
        # Create a simple 1x1 PNG image (minimal valid PNG)
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        return BytesIO(png_bytes)
    
    @pytest.mark.skip(reason="Requires S3 credentials - manual testing only")
    def test_upload_photo_success(self, client, auth_headers, test_issue, mock_image_file):
        """Test successful photo upload"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/photos",
            headers=auth_headers,
            files={"file": ("test_image.png", mock_image_file, "image/png")}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "photo_url" in data
        assert "id" in data
        assert "uploaded_at" in data
    
    def test_upload_photo_issue_not_found(self, client, auth_headers, mock_image_file):
        """Test uploading photo to non-existent issue"""
        response = client.post(
            "/api/v1/issues/RGTS-999999/photos",
            headers=auth_headers,
            files={"file": ("test_image.png", mock_image_file, "image/png")}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_upload_photo_no_auth(self, client, test_issue, mock_image_file):
        """Test uploading photo without authentication"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/photos",
            files={"file": ("test_image.png", mock_image_file, "image/png")}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.skip(reason="Requires file validation - integration test")
    def test_upload_invalid_file_type(self, client, auth_headers, test_issue):
        """Test uploading non-image file"""
        text_file = BytesIO(b"This is not an image")
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/photos",
            headers=auth_headers,
            files={"file": ("test.txt", text_file, "text/plain")}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.skip(reason="Requires file size validation - integration test")
    def test_upload_file_too_large(self, client, auth_headers, test_issue):
        """Test uploading file larger than 5MB"""
        # Create a file larger than 5MB
        large_file = BytesIO(b"0" * (6 * 1024 * 1024))
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/photos",
            headers=auth_headers,
            files={"file": ("large_image.png", large_file, "image/png")}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestListPhotos:
    """Test photo listing endpoint"""
    
    def test_list_photos_empty(self, client, auth_headers, test_issue):
        """Test listing photos when none exist"""
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/photos",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_photos_issue_not_found(self, client, auth_headers):
        """Test listing photos for non-existent issue"""
        response = client.get(
            "/api/v1/issues/RGTS-999999/photos",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_photos_no_auth(self, client, test_issue):
        """Test listing photos without authentication"""
        response = client.get(f"/api/v1/issues/{test_issue.id}/photos")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_photos_other_user_issue(self, client, auth_headers, db_session, test_admin):
        """Test regular user cannot list photos of other user's issue"""
        from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
        
        admin_issue = Issue(
            id="RGTS-666666",
            issue_number="666666",
            title="Admin Issue",
            category=IssueCategory.FLOORING,
            priority=IssuePriority.LOW,
            status=IssueStatus.OPEN,
            reported_by=test_admin.id
        )
        db_session.add(admin_issue)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/issues/{admin_issue.id}/photos",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_photos_as_admin(self, client, admin_headers, test_issue):
        """Test admin can list photos of any issue"""
        response = client.get(
            f"/api/v1/issues/{test_issue.id}/photos",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestDeletePhoto:
    """Test photo deletion endpoint"""
    
    @pytest.fixture
    def test_photo(self, db_session, test_issue):
        """Create a test photo"""
        from app.models.issue import IssuePhoto
        
        photo = IssuePhoto(
            issue_id=test_issue.id,
            photo_url="https://example.com/test_photo.jpg"
        )
        db_session.add(photo)
        db_session.commit()
        db_session.refresh(photo)
        return photo
    
    @pytest.mark.skip(reason="Requires S3 integration - manual testing only")
    def test_delete_photo_success(self, client, auth_headers, test_photo):
        """Test successful photo deletion"""
        response = client.delete(
            f"/api/v1/photos/{test_photo.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()
    
    def test_delete_photo_not_found(self, client, auth_headers):
        """Test deleting non-existent photo"""
        response = client.delete(
            "/api/v1/photos/nonexistent-photo-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_photo_no_auth(self, client, test_photo):
        """Test deleting photo without authentication"""
        response = client.delete(f"/api/v1/photos/{test_photo.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_other_user_photo(self, client, auth_headers, db_session, test_admin):
        """Test regular user cannot delete other user's photo"""
        from app.models.issue import Issue, IssuePhoto, IssueCategory, IssuePriority, IssueStatus
        
        # Create admin's issue
        admin_issue = Issue(
            id="RGTS-555555",
            issue_number="555555",
            title="Admin Issue",
            category=IssueCategory.CARPENTRY,
            priority=IssuePriority.LOW,
            status=IssueStatus.OPEN,
            reported_by=test_admin.id
        )
        db_session.add(admin_issue)
        db_session.flush()
        
        # Create photo for admin's issue
        admin_photo = IssuePhoto(
            issue_id=admin_issue.id,
            photo_url="https://example.com/admin_photo.jpg"
        )
        db_session.add(admin_photo)
        db_session.commit()
        db_session.refresh(admin_photo)
        
        response = client.delete(
            f"/api/v1/photos/{admin_photo.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.skip(reason="Requires S3 integration - manual testing only")
    def test_delete_photo_as_admin(self, client, admin_headers, test_photo):
        """Test admin can delete any photo"""
        response = client.delete(
            f"/api/v1/photos/{test_photo.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
