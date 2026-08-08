"""
Contractor Management Endpoint Tests
Tests for contractor profiles, ratings, assignments, and work completion
"""

import pytest
from fastapi import status
from app.models.contractor import ContractorProfile, AvailabilityStatus


# ==================== TEST FIXTURES ====================

@pytest.fixture(scope="function")
def contractor_profile(db_session, test_contractor):
    """Create a test contractor profile"""
    profile = ContractorProfile(
        user_id=test_contractor.id,
        company_name="ABC Electricals",
        gst_number="29ABCDE1234F1Z5",
        license_number="LIC123456",
        specializations=["electrical", "plumbing"],
        years_of_experience=5,
        is_available=True,
        availability_status=AvailabilityStatus.AVAILABLE,
        total_jobs_completed=10,
        average_rating=4.5,
        total_ratings=8,
        completion_rate=95.0,
        is_verified=True,
        is_active=True
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture(scope="function")
def second_contractor(db_session):
    """Create a second contractor user"""
    from app.models.user import User, UserRole
    from app.services.auth_service import AuthService
    
    password_hash = AuthService.get_password_hash("contractor2pass")
    contractor = User(
        email="contractor2@example.com",
        password_hash=password_hash,
        name="Second Contractor",
        phone="5559876543",
        role=UserRole.CONTRACTOR,
        is_active=True
    )
    db_session.add(contractor)
    db_session.commit()
    db_session.refresh(contractor)
    return contractor


@pytest.fixture(scope="function")
def second_contractor_profile(db_session, second_contractor):
    """Create a second contractor profile"""
    profile = ContractorProfile(
        user_id=second_contractor.id,
        company_name="XYZ Plumbing",
        gst_number="29XYZAB5678G2W6",
        specializations=["plumbing"],
        years_of_experience=3,
        is_available=True,
        availability_status=AvailabilityStatus.AVAILABLE,
        total_jobs_completed=5,
        average_rating=4.0,
        total_ratings=3,
        completion_rate=85.0,
        is_verified=False,
        is_active=True
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture(scope="function")
def assigned_issue(db_session, test_user, test_contractor):
    """Create an issue assigned to contractor"""
    from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
    
    issue = Issue(
        id="RGTS-000099",
        issue_number="000099",
        title="Assigned Issue",
        description="Issue assigned to contractor",
        category=IssueCategory.ELECTRICAL,
        priority=IssuePriority.HIGH,
        status=IssueStatus.IN_PROGRESS,
        reported_by=test_user.id,
        assigned_to=test_contractor.id
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


# ==================== CONTRACTOR PROFILE TESTS ====================

class TestCreateContractorProfile:
    """Test contractor profile creation"""
    
    def test_create_profile_success(self, client, contractor_headers, test_contractor):
        """Test successful contractor profile creation"""
        response = client.post(
            "/api/v1/contractors/",
            headers=contractor_headers,
            json={
                "company_name": "New Company",
                "gst_number": "29NEWCO1234F1Z5",
                "license_number": "LIC654321",
                "specializations": ["electrical", "painting"],
                "years_of_experience": 7
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company_name"] == "New Company"
        assert data["user_id"] == test_contractor.id
        assert data["specializations"] == ["electrical", "painting"]
        assert data["is_verified"] is False
        assert data["average_rating"] == 0.0
    
    def test_create_profile_minimal_fields(self, client, contractor_headers):
        """Test creating profile with minimal required fields"""
        response = client.post(
            "/api/v1/contractors/",
            headers=contractor_headers,
            json={
                "specializations": ["plumbing"]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["specializations"] == ["plumbing"]
        assert data["company_name"] is None
    
    def test_create_profile_duplicate(self, client, contractor_headers, contractor_profile):
        """Test creating duplicate profile fails"""
        response = client.post(
            "/api/v1/contractors/",
            headers=contractor_headers,
            json={
                "specializations": ["electrical"]
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_profile_non_contractor_role(self, client, auth_headers):
        """Test non-contractor user cannot create profile"""
        response = client.post(
            "/api/v1/contractors/",
            headers=auth_headers,
            json={
                "specializations": ["electrical"]
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_profile_duplicate_gst(self, client, contractor_headers, contractor_profile, second_contractor):
        """Test creating profile with duplicate GST number fails"""
        # Login as second contractor
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": second_contractor.email,
                "password": "contractor2pass"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/contractors/",
            headers=headers,
            json={
                "gst_number": contractor_profile.gst_number,  # Same GST as existing
                "specializations": ["plumbing"]
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "gst" in response.json()["detail"].lower()
    
    def test_create_profile_no_auth(self, client):
        """Test creating profile without authentication"""
        response = client.post(
            "/api/v1/contractors/",
            json={
                "specializations": ["electrical"]
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListContractors:
    """Test contractor listing endpoint"""
    
    def test_list_contractors_all(self, client, auth_headers, contractor_profile, second_contractor_profile):
        """Test listing all contractors"""
        response = client.get(
            "/api/v1/contractors/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
    
    def test_list_contractors_filter_by_specialization(self, client, auth_headers, contractor_profile, second_contractor_profile):
        """Test filtering contractors by specialization"""
        response = client.get(
            "/api/v1/contractors/?specialization=plumbing",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2  # Both have plumbing
        
        response = client.get(
            "/api/v1/contractors/?specialization=electrical",
            headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 1  # Only first contractor has electrical
    
    def test_list_contractors_filter_by_availability(self, client, auth_headers, contractor_profile, second_contractor_profile, db_session):
        """Test filtering contractors by availability"""
        # Make one contractor unavailable
        contractor_profile.is_available = False
        db_session.commit()
        
        response = client.get(
            "/api/v1/contractors/?is_available=true",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
    
    def test_list_contractors_filter_by_rating(self, client, auth_headers, contractor_profile, second_contractor_profile):
        """Test filtering contractors by minimum rating"""
        response = client.get(
            "/api/v1/contractors/?min_rating=4.2",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1  # Only first contractor has rating >= 4.2
        assert data["items"][0]["average_rating"] >= 4.2
    
    def test_list_contractors_filter_by_verification(self, client, auth_headers, contractor_profile, second_contractor_profile):
        """Test filtering contractors by verification status"""
        response = client.get(
            "/api/v1/contractors/?is_verified=true",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1  # Only first contractor is verified
        assert data["items"][0]["is_verified"] is True
    
    def test_list_contractors_pagination(self, client, auth_headers, contractor_profile, second_contractor_profile):
        """Test contractor list pagination"""
        response = client.get(
            "/api/v1/contractors/?skip=0&limit=1",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 1
        
        response = client.get(
            "/api/v1/contractors/?skip=1&limit=1",
            headers=auth_headers
        )
        data = response.json()
        assert len(data["items"]) == 1
    
    def test_list_contractors_no_auth(self, client):
        """Test listing contractors without authentication"""
        response = client.get("/api/v1/contractors/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetContractorDetails:
    """Test get contractor details endpoint"""
    
    def test_get_contractor_success(self, client, auth_headers, contractor_profile):
        """Test getting contractor details successfully"""
        response = client.get(
            f"/api/v1/contractors/{contractor_profile.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == contractor_profile.id
        assert data["company_name"] == "ABC Electricals"
        assert data["user"]["name"] == "Contractor User"
        assert data["average_rating"] == 4.5
    
    def test_get_contractor_not_found(self, client, auth_headers):
        """Test getting non-existent contractor"""
        response = client.get(
            "/api/v1/contractors/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_contractor_no_auth(self, client, contractor_profile):
        """Test getting contractor without authentication"""
        response = client.get(f"/api/v1/contractors/{contractor_profile.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateContractorProfile:
    """Test contractor profile update"""
    
    def test_update_own_profile_success(self, client, contractor_headers, contractor_profile):
        """Test contractor can update own profile"""
        response = client.put(
            f"/api/v1/contractors/{contractor_profile.id}",
            headers=contractor_headers,
            json={
                "company_name": "Updated Company Name",
                "specializations": ["electrical", "plumbing", "painting"],
                "is_available": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["company_name"] == "Updated Company Name"
        assert len(data["specializations"]) == 3
        assert data["is_available"] is False
    
    def test_update_profile_availability_status(self, client, contractor_headers, contractor_profile):
        """Test updating availability status"""
        response = client.put(
            f"/api/v1/contractors/{contractor_profile.id}",
            headers=contractor_headers,
            json={
                "availability_status": "on_leave"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["availability_status"] == "on_leave"
    
    def test_update_other_contractor_profile_forbidden(self, client, contractor_headers, second_contractor_profile):
        """Test contractor cannot update another contractor's profile"""
        response = client.put(
            f"/api/v1/contractors/{second_contractor_profile.id}",
            headers=contractor_headers,
            json={
                "company_name": "Hacked"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_update_any_profile(self, client, admin_headers, contractor_profile):
        """Test admin can update any contractor profile"""
        response = client.put(
            f"/api/v1/contractors/{contractor_profile.id}",
            headers=admin_headers,
            json={
                "company_name": "Admin Updated"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["company_name"] == "Admin Updated"
    
    def test_update_profile_invalid_availability_status(self, client, contractor_headers, contractor_profile):
        """Test updating with invalid availability status"""
        response = client.put(
            f"/api/v1/contractors/{contractor_profile.id}",
            headers=contractor_headers,
            json={
                "availability_status": "invalid_status"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestContractorStats:
    """Test contractor statistics endpoint"""
    
    def test_get_contractor_stats(self, client, auth_headers, contractor_profile):
        """Test getting contractor statistics"""
        response = client.get(
            f"/api/v1/contractors/{contractor_profile.id}/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["contractor_id"] == contractor_profile.id
        assert "total_jobs" in data
        assert "completed_jobs" in data
        assert "completion_rate" in data
        assert "rating_breakdown" in data
        assert "jobs_by_category" in data
    
    def test_get_stats_nonexistent_contractor(self, client, auth_headers):
        """Test getting stats for non-existent contractor"""
        response = client.get(
            "/api/v1/contractors/nonexistent-id/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestVerifyContractor:
    """Test contractor verification (admin only)"""
    
    def test_admin_verify_contractor(self, client, admin_headers, second_contractor_profile):
        """Test admin can verify contractor"""
        response = client.post(
            f"/api/v1/contractors/{second_contractor_profile.id}/verify",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_verified"] is True
        assert data["verified_at"] is not None
    
    def test_non_admin_cannot_verify(self, client, contractor_headers, second_contractor_profile):
        """Test non-admin cannot verify contractors"""
        response = client.post(
            f"/api/v1/contractors/{second_contractor_profile.id}/verify",
            headers=contractor_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_verify_nonexistent_contractor(self, client, admin_headers):
        """Test verifying non-existent contractor"""
        response = client.post(
            "/api/v1/contractors/nonexistent-id/verify",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ==================== ISSUE ASSIGNMENT TESTS ====================

class TestIssueAssignment:
    """Test issue assignment to contractors"""
    
    def test_admin_assign_issue_success(self, client, admin_headers, test_issue, test_contractor):
        """Test admin can assign issue to contractor"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/assign",
            headers=admin_headers,
            json={
                "contractor_id": test_contractor.id,
                "notes": "Urgent - needs immediate attention"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["issue_id"] == test_issue.id
        assert data["assigned_to"] == test_contractor.id
        assert data["status"] == "in_progress"
    
    def test_assign_issue_non_contractor_user(self, client, admin_headers, test_issue, test_user):
        """Test assigning issue to non-contractor user fails"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/assign",
            headers=admin_headers,
            json={
                "contractor_id": test_user.id
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "contractor role" in response.json()["detail"].lower()
    
    def test_assign_issue_nonexistent_contractor(self, client, admin_headers, test_issue):
        """Test assigning to non-existent contractor"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/assign",
            headers=admin_headers,
            json={
                "contractor_id": "nonexistent-id"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_assign_nonexistent_issue(self, client, admin_headers, test_contractor):
        """Test assigning non-existent issue"""
        response = client.post(
            "/api/v1/issues/RGTS-999999/assign",
            headers=admin_headers,
            json={
                "contractor_id": test_contractor.id
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_non_admin_cannot_assign(self, client, auth_headers, test_issue, test_contractor):
        """Test regular user cannot assign issues"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/assign",
            headers=auth_headers,
            json={
                "contractor_id": test_contractor.id
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_unassign_issue_success(self, client, admin_headers, assigned_issue):
        """Test admin can unassign contractor from issue"""
        response = client.delete(
            f"/api/v1/issues/{assigned_issue.id}/assign",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "unassigned" in response.json()["message"].lower()
    
    def test_unassign_unassigned_issue(self, client, admin_headers, test_issue):
        """Test unassigning issue with no contractor"""
        response = client.delete(
            f"/api/v1/issues/{test_issue.id}/assign",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_non_admin_cannot_unassign(self, client, contractor_headers, assigned_issue):
        """Test non-admin cannot unassign"""
        response = client.delete(
            f"/api/v1/issues/{assigned_issue.id}/assign",
            headers=contractor_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ==================== WORK COMPLETION TESTS ====================

class TestWorkCompletion:
    """Test work completion endpoints"""
    
    def test_contractor_mark_work_complete(self, client, contractor_headers, assigned_issue, contractor_profile):
        """Test contractor can mark assigned work as complete"""
        response = client.post(
            f"/api/v1/issues/{assigned_issue.id}/complete",
            headers=contractor_headers,
            json={
                "work_description": "Fixed electrical wiring in bathroom",
                "materials_used": [
                    {"name": "Wire 2.5mm", "quantity": 10, "unit": "meters", "cost": 250},
                    {"name": "MCB 32A", "quantity": 1, "unit": "piece", "cost": 120}
                ],
                "labor_cost": 500.0,
                "total_cost": 870.0,
                "after_photos": ["https://example.com/photo1.jpg"]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["issue_id"] == assigned_issue.id
        assert data["work_description"] == "Fixed electrical wiring in bathroom"
        assert float(data["total_cost"]) == 870.0
        assert data["is_verified"] is False
    
    def test_mark_complete_unassigned_issue(self, client, contractor_headers, test_issue, contractor_profile):
        """Test marking unassigned issue as complete fails"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/complete",
            headers=contractor_headers,
            json={
                "work_description": "Work done, this is more than 10 characters to meet minimum length",
                "labor_cost": 100.0,
                "total_cost": 100.0
            }
        )
        if response.status_code != status.HTTP_403_FORBIDDEN:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_mark_complete_wrong_contractor(self, client, contractor_headers, assigned_issue, second_contractor, second_contractor_profile):
        """Test different contractor cannot mark work complete"""
        # Login as second contractor
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": second_contractor.email,
                "password": "contractor2pass"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            f"/api/v1/issues/{assigned_issue.id}/complete",
            headers=headers,
            json={
                "work_description": "Work done by different contractor, more than 10 chars",
                "labor_cost": 100.0,
                "total_cost": 100.0
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_non_contractor_cannot_mark_complete(self, client, auth_headers, assigned_issue, contractor_profile):
        """Test non-contractor cannot mark work complete"""
        response = client.post(
            f"/api/v1/issues/{assigned_issue.id}/complete",
            headers=auth_headers,
            json={
                "work_description": "Work done by non-contractor user with more than 10 characters",
                "labor_cost": 100.0,
                "total_cost": 100.0
            }
        )
        if response.status_code != status.HTTP_403_FORBIDDEN:
            import json
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWorkVerification:
    """Test work completion verification"""
    
    @pytest.fixture
    def completed_work(self, db_session, assigned_issue, contractor_profile):
        """Create a completed work record"""
        from app.models.contractor import WorkCompletion
        from datetime import datetime
        
        work = WorkCompletion(
            issue_id=assigned_issue.id,
            contractor_id=contractor_profile.id,
            completed_at=datetime.utcnow(),
            work_description="Work completed",
            total_cost=500,
            is_verified=False
        )
        db_session.add(work)
        db_session.commit()
        db_session.refresh(work)
        return work
    
    def test_admin_verify_work_success(self, client, admin_headers, completed_work):
        """Test admin can verify completed work"""
        response = client.post(
            f"/api/v1/work-completions/{completed_work.id}/verify",
            headers=admin_headers,
            json={
                "is_approved": True,
                "verification_notes": "Work quality is excellent"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_verified"] is True
        assert data["verification_notes"] == "Work quality is excellent"
    
    def test_admin_reject_work(self, client, admin_headers, completed_work):
        """Test admin can reject completed work"""
        response = client.post(
            f"/api/v1/work-completions/{completed_work.id}/verify",
            headers=admin_headers,
            json={
                "is_approved": False,
                "verification_notes": "Work needs improvement"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_verified"] is False
    
    def test_non_admin_cannot_verify(self, client, contractor_headers, completed_work):
        """Test non-admin cannot verify work"""
        response = client.post(
            f"/api/v1/work-completions/{completed_work.id}/verify",
            headers=contractor_headers,
            json={
                "is_approved": True
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_verify_nonexistent_work(self, client, admin_headers):
        """Test verifying non-existent work completion"""
        response = client.post(
            "/api/v1/work-completions/nonexistent-id/verify",
            headers=admin_headers,
            json={
                "is_approved": True
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ==================== CONTRACTOR RATING TESTS ====================

class TestContractorRating:
    """Test contractor rating system"""
    
    @pytest.fixture
    def completed_and_verified_work(self, db_session, assigned_issue, contractor_profile, test_admin):
        """Create verified work completion"""
        from app.models.contractor import WorkCompletion
        from datetime import datetime
        
        work = WorkCompletion(
            issue_id=assigned_issue.id,
            contractor_id=contractor_profile.id,
            completed_at=datetime.utcnow(),
            work_description="Work completed",
            total_cost=500,
            is_verified=True,
            verified_by=test_admin.id,
            verified_at=datetime.utcnow()
        )
        db_session.add(work)
        db_session.commit()
        db_session.refresh(work)
        return work
    
    def test_issue_reporter_can_rate(self, client, auth_headers, contractor_profile, assigned_issue, completed_and_verified_work):
        """Test issue reporter can rate contractor"""
        response = client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 5,
                "quality_rating": 5,
                "punctuality_rating": 4,
                "professionalism_rating": 5,
                "review_text": "Excellent work! Very professional."
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] == 5
        assert data["contractor_id"] == contractor_profile.id
        assert data["issue_id"] == assigned_issue.id
    
    def test_rate_without_work_completion(self, client, auth_headers, contractor_profile, assigned_issue):
        """Test rating without work completion fails"""
        response = client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 5
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "complete" in response.json()["detail"].lower()
    
    def test_non_reporter_cannot_rate(self, client, contractor_headers, contractor_profile, assigned_issue, completed_and_verified_work):
        """Test non-reporter cannot rate contractor"""
        response = client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=contractor_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 5
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_duplicate_rating_prevented(self, client, auth_headers, contractor_profile, assigned_issue, completed_and_verified_work):
        """Test duplicate rating for same issue is prevented"""
        # First rating
        client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 5
            }
        )
        
        # Duplicate rating
        response = client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 4
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_get_contractor_ratings(self, client, auth_headers, contractor_profile, assigned_issue, completed_and_verified_work):
        """Test getting contractor ratings list"""
        # Create a rating first
        client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 5,
                "review_text": "Great work!"
            }
        )
        
        # Get ratings
        response = client.get(
            f"/api/v1/contractors/{contractor_profile.id}/ratings",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["rating"] == 5
    
    def test_invalid_rating_value(self, client, auth_headers, contractor_profile, assigned_issue, completed_and_verified_work):
        """Test invalid rating value"""
        response = client.post(
            f"/api/v1/contractors/{contractor_profile.id}/rate",
            headers=auth_headers,
            json={
                "issue_id": assigned_issue.id,
                "rating": 6  # Invalid - should be 1-5
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
