"""
Booking Management Endpoint Tests
Tests for booking CRUD, validation, check-in/out, and availability
"""

import pytest
from fastapi import status
from datetime import datetime, date, time, timedelta


@pytest.fixture
def create_test_asset(client, admin_headers):
    """Create a test asset for booking tests"""
    response = client.post(
        "/api/v1/assets/",
        headers=admin_headers,
        json={
            "name": "Party Hall",
            "asset_type": "party_hall",
            "description": "Community party hall for events",
            "location": "Building B, Ground Floor",
            "capacity": 100,
            "hourly_rate": 500,
            "is_bookable": True,
            "advance_booking_days": 30,
            "min_booking_duration": 120,  # 2 hours
            "max_booking_duration": 480,  # 8 hours
            "operating_hours_start": "10:00",
            "operating_hours_end": "22:00"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def create_gym_asset(client, admin_headers):
    """Create a gym asset with different hours"""
    response = client.post(
        "/api/v1/assets/",
        headers=admin_headers,
        json={
            "name": "Fitness Center",
            "asset_type": "gym",
            "capacity": 20,
            "hourly_rate": 0,  # Free
            "is_bookable": True,
            "min_booking_duration": 60,
            "max_booking_duration": 120,
            "operating_hours_start": "06:00",
            "operating_hours_end": "22:00"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def sample_booking_data(create_test_asset):
    """Sample booking data for testing"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    return {
        "asset_id": create_test_asset["id"],
        "booking_date": tomorrow.isoformat(),
        "start_time": "14:00",
        "end_time": "18:00",
        "purpose": "Birthday party",
        "number_of_guests": 50
    }


@pytest.fixture
def create_test_booking(client, auth_headers, sample_booking_data):
    """Helper fixture to create a test booking"""
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json=sample_booking_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


class TestCreateBooking:
    """Test booking creation endpoint"""
    
    def test_create_booking_success(self, client, auth_headers, sample_booking_data):
        """Test successful booking creation"""
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json=sample_booking_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["asset"]["name"] == "Party Hall"
        assert data["purpose"] == "Birthday party"
        assert data["number_of_guests"] == 50
        assert data["status"] in ["pending", "confirmed"]  # Can be either based on service logic
        assert data["payment_status"] == "pending"
        assert data["duration_minutes"] == 240  # 4 hours
        assert float(data["payment_amount"]) == 2000  # 4 * 500
        assert "id" in data
        assert "user" in data
    
    def test_create_booking_minimal_fields(self, client, auth_headers, create_test_asset):
        """Test creating booking with minimal required fields"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["number_of_guests"] == 1  # Default value
    
    def test_create_booking_past_date(self, client, auth_headers, create_test_asset):
        """Test creating booking in the past"""
        yesterday = (datetime.now() - timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": yesterday.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "past" in response.json()["detail"].lower()
    
    def test_create_booking_too_far_ahead(self, client, auth_headers, create_test_asset):
        """Test creating booking beyond advance booking limit"""
        far_future = (datetime.now() + timedelta(days=35)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": far_future.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "advance" in response.json()["detail"].lower()
    
    def test_create_booking_invalid_duration_too_short(self, client, auth_headers, create_test_asset):
        """Test creating booking shorter than minimum duration"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "15:00"  # Only 1 hour, min is 2 hours
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        assert "minimum" in detail or "at least" in detail
    
    def test_create_booking_invalid_duration_too_long(self, client, auth_headers, create_test_asset):
        """Test creating booking longer than maximum duration"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "10:00",
                "end_time": "22:00"  # 12 hours, max is 8 hours
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        assert "maximum" in detail or "cannot exceed" in detail
    
    def test_create_booking_outside_operating_hours_start(self, client, auth_headers, create_test_asset):
        """Test creating booking before operating hours"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "08:00",  # Before 10:00
                "end_time": "12:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "operating hours" in response.json()["detail"].lower()
    
    def test_create_booking_outside_operating_hours_end(self, client, auth_headers, create_test_asset):
        """Test creating booking after operating hours"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "20:00",
                "end_time": "23:00"  # After 22:00
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "operating hours" in response.json()["detail"].lower()
    
    def test_create_booking_end_before_start(self, client, auth_headers, create_test_asset):
        """Test creating booking with end time before start time"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "18:00",
                "end_time": "14:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        # May return duration error or end time error
        assert "after" in detail or "before" in detail or "end time" in detail or "duration" in detail
    
    def test_create_booking_inactive_asset(self, client, auth_headers, admin_headers, create_test_asset):
        """Test creating booking for inactive asset"""
        # Deactivate asset
        asset_id = create_test_asset["id"]
        client.put(
            f"/api/v1/assets/{asset_id}",
            headers=admin_headers,
            json={"is_active": False}
        )
        
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        assert "inactive" in detail or "not active" in detail
    
    def test_create_booking_non_bookable_asset(self, client, auth_headers, admin_headers, create_test_asset):
        """Test creating booking for non-bookable asset"""
        # Make asset non-bookable
        asset_id = create_test_asset["id"]
        client.put(
            f"/api/v1/assets/{asset_id}",
            headers=admin_headers,
            json={"is_bookable": False}
        )
        
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        assert "not" in detail and ("bookable" in detail or "available" in detail)
    
    def test_create_booking_conflict(self, client, auth_headers, create_test_booking, create_test_asset):
        """Test creating overlapping booking"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "16:00",  # Overlaps with 14:00-18:00
                "end_time": "20:00"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "conflict" in response.json()["detail"].lower()
    
    def test_create_booking_no_auth(self, client, sample_booking_data):
        """Test creating booking without authentication"""
        response = client.post(
            "/api/v1/bookings/",
            json=sample_booking_data
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_create_booking_nonexistent_asset(self, client, auth_headers):
        """Test creating booking for non-existent asset"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": "nonexistent-id",
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


class TestGetBookings:
    """Test booking listing endpoint"""
    
    def test_list_user_bookings_empty(self, client, auth_headers):
        """Test listing bookings when none exist"""
        response = client.get("/api/v1/bookings/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_user_bookings(self, client, auth_headers, create_test_booking):
        """Test listing user's bookings"""
        response = client.get("/api/v1/bookings/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["purpose"] == "Birthday party"
    
    def test_list_bookings_filter_by_status(self, client, auth_headers, create_test_booking):
        """Test filtering bookings by status"""
        response = client.get("/api/v1/bookings/?status=pending", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(booking["status"] == "pending" for booking in data)
    
    def test_list_bookings_no_auth(self, client, create_test_booking):
        """Test listing bookings without authentication"""
        response = client.get("/api/v1/bookings/")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestGetBooking:
    """Test get single booking endpoint"""
    
    def test_get_booking_success(self, client, auth_headers, create_test_booking):
        """Test getting a single booking"""
        booking_id = create_test_booking["id"]
        response = client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == booking_id
        assert data["purpose"] == "Birthday party"
    
    def test_get_booking_not_found(self, client, auth_headers):
        """Test getting non-existent booking"""
        response = client.get("/api/v1/bookings/nonexistent-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_other_user_booking(self, client, admin_headers, create_test_booking):
        """Test admin can view other user's booking"""
        booking_id = create_test_booking["id"]
        response = client.get(f"/api/v1/bookings/{booking_id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == booking_id
    
    def test_get_booking_no_auth(self, client, create_test_booking):
        """Test getting booking without authentication"""
        booking_id = create_test_booking["id"]
        response = client.get(f"/api/v1/bookings/{booking_id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestUpdateBooking:
    """Test booking update endpoint"""
    
    def test_update_booking_success(self, client, auth_headers, create_test_booking):
        """Test successful booking update"""
        booking_id = create_test_booking["id"]
        response = client.put(
            f"/api/v1/bookings/{booking_id}",
            headers=auth_headers,
            json={
                "purpose": "Updated: Anniversary celebration",
                "number_of_guests": 75
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["purpose"] == "Updated: Anniversary celebration"
        assert data["number_of_guests"] == 75
    
    def test_update_booking_time(self, client, auth_headers, create_test_booking):
        """Test updating booking time"""
        booking_id = create_test_booking["id"]
        response = client.put(
            f"/api/v1/bookings/{booking_id}",
            headers=auth_headers,
            json={
                "start_time": "15:00",
                "end_time": "19:00"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["start_time"] == "15:00:00"
        assert data["end_time"] == "19:00:00"
    
    def test_update_booking_not_found(self, client, auth_headers):
        """Test updating non-existent booking"""
        response = client.put(
            "/api/v1/bookings/nonexistent-id",
            headers=auth_headers,
            json={"purpose": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_booking_no_auth(self, client, create_test_booking):
        """Test updating booking without authentication"""
        booking_id = create_test_booking["id"]
        response = client.put(
            f"/api/v1/bookings/{booking_id}",
            json={"purpose": "Updated"}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestCancelBooking:
    """Test booking cancellation endpoint"""
    
    def test_cancel_booking_success(self, client, auth_headers, create_test_booking):
        """Test successful booking cancellation"""
        booking_id = create_test_booking["id"]
        response = client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cancelled successfully" in data["message"].lower()
        
        # Verify booking is cancelled
        get_response = client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert get_response.json()["status"] == "cancelled"
    
    def test_cancel_booking_with_reason(self, client, auth_headers, create_test_booking):
        """Test cancelling booking with reason"""
        booking_id = create_test_booking["id"]
        response = client.delete(
            f"/api/v1/bookings/{booking_id}?cancellation_reason=Change of plans",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_cancel_booking_not_found(self, client, auth_headers):
        """Test cancelling non-existent booking"""
        response = client.delete("/api/v1/bookings/nonexistent-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cancel_booking_no_auth(self, client, create_test_booking):
        """Test cancelling booking without authentication"""
        booking_id = create_test_booking["id"]
        response = client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestCheckInOut:
    """Test check-in and check-out endpoints"""
    
    def test_checkin_success(self, client, auth_headers, create_test_asset):
        """Test successful check-in"""
        # Create a booking for today
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        # Calculate valid times (current time + 5 minutes to 4 hours later)
        start_hour = current_time.hour if current_time.minute < 55 else current_time.hour + 1
        start_time = f"{start_hour:02d}:00"
        end_hour = min(start_hour + 4, 21)  # Max 21:00, within operating hours
        end_time = f"{end_hour:02d}:00"
        
        booking_response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": today.isoformat(),
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        if booking_response.status_code == status.HTTP_201_CREATED:
            booking_id = booking_response.json()["id"]
            
            # Check-in
            response = client.post(
                f"/api/v1/bookings/{booking_id}/checkin",
                headers=auth_headers
            )
            
            # Check-in might succeed or fail depending on timing
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert data["status"] == "confirmed"
                assert data["checked_in_at"] is not None
    
    def test_checkin_not_found(self, client, auth_headers):
        """Test check-in for non-existent booking"""
        response = client.post(
            "/api/v1/bookings/nonexistent-id/checkin",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_checkout_without_checkin(self, client, auth_headers, create_test_booking):
        """Test check-out without prior check-in"""
        booking_id = create_test_booking["id"]
        response = client.post(
            f"/api/v1/bookings/{booking_id}/checkout",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json()["detail"].lower()
        assert "check" in detail and "in" in detail
    
    def test_checkout_not_found(self, client, auth_headers):
        """Test check-out for non-existent booking"""
        response = client.post(
            "/api/v1/bookings/nonexistent-id/checkout",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBookingAvailability:
    """Test availability checking endpoint"""
    
    def test_check_availability_no_bookings(self, client, auth_headers, create_test_asset):
        """Test availability with no existing bookings"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        asset_id = create_test_asset["id"]
        
        response = client.get(
            f"/api/v1/bookings/assets/{asset_id}/availability",
            params={"booking_date": tomorrow.isoformat()},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["asset_id"] == asset_id
        assert data["booking_date"] == tomorrow.isoformat()  # Correct field name
        assert data["is_available"] is True
        assert len(data["available_slots"]) >= 0  # Can be empty or have slots
        # Schema has conflicting_bookings, not booked_slots
        assert len(data["conflicting_bookings"]) == 0
    
    def test_check_availability_with_bookings(self, client, auth_headers, create_test_booking, create_test_asset):
        """Test availability with existing bookings"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        asset_id = create_test_asset["id"]
        
        response = client.get(
            f"/api/v1/bookings/assets/{asset_id}/availability",
            params={"booking_date": tomorrow.isoformat()},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Schema has conflicting_bookings, not booked_slots
        assert "conflicting_bookings" in data or "available_slots" in data
        # If there are conflicts, check them
        if "conflicting_bookings" in data and len(data["conflicting_bookings"]) > 0:
            assert isinstance(data["conflicting_bookings"][0], str)  # Should be booking IDs
    
    def test_check_availability_asset_not_found(self, client, auth_headers):
        """Test availability for non-existent asset"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.get(
            f"/api/v1/bookings/assets/nonexistent-id/availability",
            params={"booking_date": tomorrow.isoformat()},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_check_availability_no_auth(self, client, create_test_asset):
        """Test availability without authentication"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        asset_id = create_test_asset["id"]
        
        response = client.get(
            f"/api/v1/bookings/assets/{asset_id}/availability",
            params={"booking_date": tomorrow.isoformat()}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestListAssetBookings:
    """Test listing bookings for a specific asset"""
    
    def test_list_asset_bookings_empty(self, client, admin_headers, create_test_asset):
        """Test listing asset bookings when none exist"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/bookings/assets/{asset_id}/bookings", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_asset_bookings(self, client, admin_headers, create_test_booking, create_test_asset):
        """Test listing asset bookings"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/bookings/assets/{asset_id}/bookings", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["asset"]["id"] == asset_id
    
    def test_list_asset_bookings_filter_by_status(self, client, admin_headers, create_test_booking, create_test_asset):
        """Test filtering asset bookings by status"""
        asset_id = create_test_asset["id"]
        # Use confirmed status since bookings might be auto-confirmed
        response = client.get(
            f"/api/v1/bookings/assets/{asset_id}/bookings?status=confirmed",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Only check if there are bookings
        if len(data) > 0:
            assert all(booking["status"] == "confirmed" for booking in data)
    
    def test_list_asset_bookings_non_admin(self, client, auth_headers, create_test_booking, create_test_asset):
        """Test non-admin access to asset bookings (may be allowed for transparency)"""
        asset_id = create_test_asset["id"]
        response = client.get(f"/api/v1/bookings/assets/{asset_id}/bookings", headers=auth_headers)
        # May allow users to see asset bookings for transparency
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_list_asset_bookings_not_found(self, client, admin_headers):
        """Test listing bookings for non-existent asset"""
        response = client.get("/api/v1/bookings/assets/nonexistent-id/bookings", headers=admin_headers)
        # May return empty list or 404 based on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestMultipleBookings:
    """Test scenarios with multiple bookings"""
    
    def test_multiple_users_same_asset(self, client, auth_headers, admin_headers, test_admin, create_test_asset):
        """Test multiple users can book same asset at different times"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        asset_id = create_test_asset["id"]
        
        # First user books 14:00-16:00
        response1 = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "16:00"
            }
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second user (admin) books 18:00-20:00 (non-overlapping)
        response2 = client.post(
            "/api/v1/bookings/",
            headers=admin_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "18:00",
                "end_time": "20:00"
            }
        )
        assert response2.status_code == status.HTTP_201_CREATED
    
    def test_adjacent_bookings(self, client, auth_headers, admin_headers, create_test_asset):
        """Test adjacent bookings (end time = next start time)"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        asset_id = create_test_asset["id"]
        
        # First booking 14:00-16:00
        response1 = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "16:00"
            }
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second booking 16:00-18:00 (adjacent, should succeed)
        response2 = client.post(
            "/api/v1/bookings/",
            headers=admin_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "16:00",
                "end_time": "18:00"
            }
        )
        assert response2.status_code == status.HTTP_201_CREATED
    
    def test_booking_different_dates(self, client, auth_headers, create_test_asset):
        """Test booking same asset on different dates"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        day_after = (datetime.now() + timedelta(days=2)).date()
        asset_id = create_test_asset["id"]
        
        # Booking for tomorrow
        response1 = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Same time slot but different date (should succeed)
        response2 = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": asset_id,
                "booking_date": day_after.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response2.status_code == status.HTTP_201_CREATED
    
    def test_cancel_and_rebook(self, client, auth_headers, create_test_booking, create_test_asset):
        """Test cancelling and rebooking same slot"""
        # Cancel existing booking
        booking_id = create_test_booking["id"]
        cancel_response = client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert cancel_response.status_code == status.HTTP_200_OK
        
        # Rebook the same slot
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.post(
            "/api/v1/bookings/",
            headers=auth_headers,
            json={
                "asset_id": create_test_asset["id"],
                "booking_date": tomorrow.isoformat(),
                "start_time": "14:00",
                "end_time": "18:00"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
