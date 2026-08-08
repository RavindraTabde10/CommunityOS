"""
Asset Management Endpoint Tests
Tests for asset CRUD operations, QR codes, and statistics
"""

import pytest
from fastapi import status
from datetime import time


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing"""
    return {
        "name": "Swimming Pool",
        "asset_type": "pool",
        "description": "Olympic-sized swimming pool with diving board",
        "location": "Building A, Ground Floor",
        "capacity": 50,
        "hourly_rate": 0,
        "is_bookable": True,
        "advance_booking_days": 30,
        "min_booking_duration": 60,
        "max_booking_duration": 180,
        "operating_hours_start": "06:00",
        "operating_hours_end": "22:00"
    }


@pytest.fixture
def create_test_asset(client, admin_headers, sample_asset_data):
    """Helper fixture to create a test asset"""
    response = client.post(
        "/api/v1/assets/",
        headers=admin_headers,
        json=sample_asset_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


class TestCreateAsset:
    """Test asset creation endpoint"""
    
    def test_create_asset_success(self, client, admin_headers, sample_asset_data):
        """Test successful asset creation by admin"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json=sample_asset_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Swimming Pool"
        assert data["asset_type"] == "pool"
        assert data["capacity"] == 50
        assert data["is_active"] is True
        assert data["is_bookable"] is True
        assert "id" in data
        assert "qr_code_data" in data
        assert "created_at" in data
    
    def test_create_asset_minimal_fields(self, client, admin_headers):
        """Test creating asset with minimal required fields"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={
                "name": "Gym",
                "asset_type": "gym"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Gym"
        assert data["asset_type"] == "gym"
        assert data["is_bookable"] is True  # Default value
        assert float(data["hourly_rate"]) == 0.0  # Default value (formatted as Decimal)
    
    def test_create_asset_all_types(self, client, admin_headers):
        """Test creating assets of all valid types"""
        asset_types = ["gym", "pool", "clubhouse", "party_hall", "sports_court", "meeting_room", "parking", "other"]
        
        for asset_type in asset_types:
            response = client.post(
                "/api/v1/assets/",
                headers=admin_headers,
                json={
                    "name": f"Test {asset_type}",
                    "asset_type": asset_type
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["asset_type"] == asset_type
    
    def test_create_asset_invalid_type(self, client, admin_headers):
        """Test creating asset with invalid type"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={
                "name": "Test Asset",
                "asset_type": "invalid_type"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_asset_no_auth(self, client, sample_asset_data):
        """Test creating asset without authentication"""
        response = client.post(
            "/api/v1/assets/",
            json=sample_asset_data
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_create_asset_non_admin(self, client, auth_headers, sample_asset_data):
        """Test creating asset as non-admin user"""
        response = client.post(
            "/api/v1/assets/",
            headers=auth_headers,
            json=sample_asset_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_asset_invalid_capacity(self, client, admin_headers):
        """Test creating asset with invalid capacity"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={
                "name": "Test Asset",
                "asset_type": "gym",
                "capacity": -5
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_asset_invalid_hourly_rate(self, client, admin_headers):
        """Test creating asset with negative hourly rate"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={
                "name": "Test Asset",
                "asset_type": "party_hall",
                "hourly_rate": -100
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_asset_with_operating_hours(self, client, admin_headers):
        """Test creating asset with operating hours"""
        response = client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={
                "name": "Meeting Room",
                "asset_type": "meeting_room",
                "operating_hours_start": "09:00",
                "operating_hours_end": "18:00"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["operating_hours_start"] == "09:00:00"
        assert data["operating_hours_end"] == "18:00:00"


class TestGetAssets:
    """Test asset listing endpoint"""
    
    def test_list_assets_empty(self, client, auth_headers):
        """Test listing assets when none exist"""
        response = client.get("/api/v1/assets/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_assets(self, client, auth_headers, create_test_asset):
        """Test listing assets"""
        response = client.get("/api/v1/assets/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Swimming Pool"
    
    def test_list_assets_filter_by_type(self, client, admin_headers, auth_headers):
        """Test filtering assets by type"""
        # Create assets of different types
        client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={"name": "Gym", "asset_type": "gym"}
        )
        client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={"name": "Pool", "asset_type": "pool"}
        )
        
        # Filter by gym
        response = client.get("/api/v1/assets/?asset_type=gym", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["asset_type"] == "gym"
    
    def test_list_assets_filter_bookable(self, client, admin_headers, auth_headers):
        """Test filtering bookable assets only"""
        # Create bookable and non-bookable assets
        client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={"name": "Bookable Gym", "asset_type": "gym", "is_bookable": True}
        )
        client.post(
            "/api/v1/assets/",
            headers=admin_headers,
            json={"name": "Non-bookable Parking", "asset_type": "parking", "is_bookable": False}
        )
        
        # Filter bookable only
        response = client.get("/api/v1/assets/?is_bookable=true", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(asset["is_bookable"] for asset in data)
    
    def test_list_assets_no_auth(self, client, create_test_asset):
        """Test listing assets without authentication"""
        response = client.get("/api/v1/assets/")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestGetAsset:
    """Test get single asset endpoint"""
    
    def test_get_asset_success(self, client, auth_headers, create_test_asset):
        """Test getting a single asset"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/assets/{asset_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == asset_id
        assert data["name"] == "Swimming Pool"
        assert "qr_code_data" in data
    
    def test_get_asset_not_found(self, client, auth_headers):
        """Test getting non-existent asset"""
        response = client.get("/api/v1/assets/nonexistent-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_asset_no_auth(self, client, create_test_asset):
        """Test getting asset without authentication"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/assets/{asset_id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestUpdateAsset:
    """Test asset update endpoint"""
    
    def test_update_asset_success(self, client, admin_headers, create_test_asset):
        """Test successful asset update"""
        asset_id = create_test_asset["id"]
        response = client.put(
            f"/api/v1/assets/{asset_id}",
            headers=admin_headers,
            json={
                "name": "Updated Pool Name",
                "capacity": 75,
                "hourly_rate": 100
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Pool Name"
        assert data["capacity"] == 75
        assert float(data["hourly_rate"]) == 100.0  # Decimal formatted as string
    
    def test_update_asset_partial(self, client, admin_headers, create_test_asset):
        """Test partial asset update"""
        asset_id = create_test_asset["id"]
        response = client.put(
            f"/api/v1/assets/{asset_id}",
            headers=admin_headers,
            json={"description": "Updated description only"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description only"
        assert data["name"] == "Swimming Pool"  # Unchanged
    
    def test_update_asset_deactivate(self, client, admin_headers, create_test_asset):
        """Test deactivating an asset"""
        asset_id = create_test_asset["id"]
        response = client.put(
            f"/api/v1/assets/{asset_id}",
            headers=admin_headers,
            json={"is_active": False}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False
    
    def test_update_asset_not_found(self, client, admin_headers):
        """Test updating non-existent asset"""
        response = client.put(
            "/api/v1/assets/nonexistent-id",
            headers=admin_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_asset_non_admin(self, client, auth_headers, create_test_asset):
        """Test updating asset as non-admin user"""
        asset_id = create_test_asset["id"]
        response = client.put(
            f"/api/v1/assets/{asset_id}",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_asset_no_auth(self, client, create_test_asset):
        """Test updating asset without authentication"""
        asset_id = create_test_asset["id"]
        response = client.put(
            f"/api/v1/assets/{asset_id}",
            json={"name": "Updated"}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestDeleteAsset:
    """Test asset deletion endpoint"""
    
    def test_delete_asset_success(self, client, admin_headers, create_test_asset):
        """Test successful asset deletion (soft delete)"""
        asset_id = create_test_asset["id"]
        response = client.delete(f"/api/v1/assets/{asset_id}", headers=admin_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]  # Either is acceptable
        
        # Verify asset is deactivated
        get_response = client.get(f"/api/v1/assets/{asset_id}", headers=admin_headers)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["is_active"] is False
    
    def test_delete_asset_not_found(self, client, admin_headers):
        """Test deleting non-existent asset"""
        response = client.delete("/api/v1/assets/nonexistent-id", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_asset_non_admin(self, client, auth_headers, create_test_asset):
        """Test deleting asset as non-admin user"""
        asset_id = create_test_asset["id"]
        response = client.delete(f"/api/v1/assets/{asset_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_asset_no_auth(self, client, create_test_asset):
        """Test deleting asset without authentication"""
        asset_id = create_test_asset["id"]
        response = client.delete(f"/api/v1/assets/{asset_id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestAssetQRCode:
    """Test QR code generation and scanning"""
    
    def test_generate_qr_code_success(self, client, admin_headers, create_test_asset):
        """Test QR code generation"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/assets/{asset_id}/qrcode", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "qr_code_data" in data  # The QR code data string
        assert "asset_id" in data
        assert "asset_name" in data
        assert data["asset_name"] == "Swimming Pool"
        # QR code data should be a base64-encoded PNG image
        assert len(data["qr_code_data"]) > 0
    
    def test_generate_qr_code_not_found(self, client, admin_headers):
        """Test QR code generation for non-existent asset"""
        response = client.get("/api/v1/assets/nonexistent-id/qrcode", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_scan_qr_code_success(self, client, auth_headers, create_test_asset):
        """Test QR code scanning"""
        qr_data = create_test_asset["qr_code_data"]
        response = client.post(
            "/api/v1/assets/scan",
            headers=auth_headers,
            json={"qr_code_data": qr_data}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "asset" in data
        assert data["asset"]["name"] == "Swimming Pool"
        assert data["asset"]["id"] == create_test_asset["id"]
    
    def test_scan_qr_code_invalid(self, client, auth_headers):
        """Test scanning invalid QR code"""
        response = client.post(
            "/api/v1/assets/scan",
            headers=auth_headers,
            json={"qr_code_data": "invalid-qr-data"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAssetStats:
    """Test asset statistics endpoint"""
    
    def test_get_asset_stats_no_bookings(self, client, admin_headers, create_test_asset):
        """Test asset statistics with no bookings"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/assets/{asset_id}/stats", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["asset_id"] == asset_id
        assert data["asset_name"] == "Swimming Pool"
        assert data["total_bookings"] == 0
        assert data["completed_bookings"] == 0
        assert data["cancelled_bookings"] == 0
        assert float(data["total_revenue"]) == 0.0  # Decimal formatted as string
        assert data["average_booking_duration"] == 0.0  # Correct field name
        assert data["occupancy_rate"] == 0.0
    
    def test_get_asset_stats_not_found(self, client, admin_headers):
        """Test statistics for non-existent asset"""
        response = client.get("/api/v1/assets/nonexistent-id/stats", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_asset_stats_non_admin(self, client, auth_headers, create_test_asset):
        """Test getting stats as non-admin user"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/assets/{asset_id}/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
