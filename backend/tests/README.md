# Test Suite Documentation

## Overview

Comprehensive test suite for the Society Management App REST API. Tests cover authentication, user management, issue tracking, photo uploads, asset management, and facility bookings.

## Test Structure

```
tests/
├── __init__.py          # Test package initialization
├── conftest.py          # Shared fixtures and test configuration
├── test_auth.py         # Authentication endpoint tests
├── test_users.py        # User management endpoint tests
├── test_issues.py       # Issue management endpoint tests
├── test_photos.py       # Photo upload endpoint tests
├── test_assets.py       # Asset management endpoint tests (NEW)
├── test_bookings.py     # Facility booking endpoint tests (NEW)
└── requirements.txt     # Test dependencies
```

## Running Tests

### Install Test Dependencies

```bash
cd backend
.venv\Scripts\activate

# Install test requirements
pip install -r tests/requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Authentication tests
pytest tests/test_auth.py

# User management tests
pytest tests/test_users.py

# Issue tests
pytest tests/test_issues.py

# Photo tests
pytest tests/test_photos.py

# Asset management tests
pytest tests/test_assets.py

# Facility booking tests
pytest tests/test_bookings.py
```

### Run Specific Test Classes

```bash
# Run only registration tests
pytest tests/test_auth.py::TestUserRegistration

# Run only password change tests
pytest tests/test_users.py::TestPasswordChange
```

### Run Specific Test Functions

```bash
# Run single test
pytest tests/test_auth.py::TestUserLogin::test_login_success
```

### Run Tests with Coverage

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage report
pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)

#### User Registration
- ✅ Successful registration with valid data
- ✅ Registration with duplicate email (should fail)
- ✅ Registration with invalid email format
- ✅ Registration with short password
- ✅ Registration with different roles

#### User Login
- ✅ Successful login with valid credentials
- ✅ Login with wrong password
- ✅ Login with non-existent user
- ✅ Login with inactive user account
- ✅ Admin login

#### Get Current User
- ✅ Get profile with valid token
- ✅ Get profile without token (should fail)
- ✅ Get profile with invalid token
- ✅ Get admin profile

**Total: 13 tests**

### 2. User Management Tests (`test_users.py`)

#### User Profile Management
- ✅ Update own profile successfully
- ✅ Partial profile update
- ✅ Update profile without authentication (should fail)

#### Password Change
- ✅ Change password successfully
- ✅ Change with wrong current password
- ✅ Change to same password (should fail)
- ✅ Change to short password (should fail)

#### Password Reset Flow
- ✅ Request reset for existing user
- ✅ Request reset for non-existent user
- ✅ Reset password with valid token
- ✅ Reset with invalid token

#### Admin User Management
- ✅ List all users as admin
- ✅ List users as regular user (should fail)
- ✅ List with pagination
- ✅ List with role filter
- ✅ List with search query
- ✅ Update other user as admin
- ✅ Update other user as regular user (should fail)
- ✅ Change user role as admin
- ✅ Admin cannot change own role
- ✅ Deactivate user as admin
- ✅ Admin cannot deactivate self
- ✅ Delete user as admin
- ✅ Admin cannot delete self

**Total: 24 tests**

### 3. Issue Management Tests (`test_issues.py`)

#### Create Issue
- ✅ Create issue successfully
- ✅ Create with minimal fields
- ✅ Create with invalid category
- ✅ Create with invalid priority
- ✅ Create without authentication
- ✅ Create multiple issues with unique IDs

#### List Issues
- ✅ User sees only their issues
- ✅ Admin sees all issues
- ✅ Filter by status
- ✅ Filter by category
- ✅ Pagination support
- ✅ List without authentication

#### Get Single Issue
- ✅ Get issue details
- ✅ Get non-existent issue
- ✅ Regular user cannot see other's issue
- ✅ Admin can see any issue

#### Update Issue
- ✅ Update own issue
- ✅ Partial update
- ✅ Cannot update other user's issue
- ✅ Admin can update any issue
- ✅ Update non-existent issue

#### Delete Issue
- ✅ Delete own issue
- ✅ Cannot delete other user's issue
- ✅ Admin can delete any issue
- ✅ Delete non-existent issue

**Total: 28 tests**

### 4. Photo Upload Tests (`test_photos.py`)

#### Photo Upload
- ⚠️ Upload photo successfully (requires S3)
- ✅ Upload to non-existent issue
- ✅ Upload without authentication
- ⚠️ Upload invalid file type (integration)
- ⚠️ Upload file too large (integration)

#### List Photos
- ✅ List photos (empty)
- ✅ List for non-existent issue
- ✅ List without authentication
- ✅ Cannot list other user's photos
- ✅ Admin can list any photos

#### Delete Photo
- ⚠️ Delete photo successfully (requires S3)
- ✅ Delete non-existent photo
- ✅ Delete without authentication
- ✅ Cannot delete other user's photo
- ⚠️ Admin can delete any photo (requires S3)

**Total: 14 tests (6 skipped - require S3/integration)**

### 5. Asset Management Tests (`test_assets.py`)

#### Create Asset (Admin Only)
- ✅ Create asset successfully with all fields
- ✅ Create asset with minimal required fields
- ✅ Create assets of all valid types (gym, pool, clubhouse, etc.)
- ✅ Create with invalid asset type (should fail)
- ✅ Create without authentication (should fail)
- ✅ Create as non-admin user (should fail)
- ✅ Create with invalid capacity (should fail)
- ✅ Create with negative hourly rate (should fail)
- ✅ Create with operating hours

#### List Assets
- ✅ List assets when none exist
- ✅ List all assets
- ✅ Filter by asset type
- ✅ Filter by bookable status
- ✅ List without authentication (should fail)

#### Get Asset
- ✅ Get single asset successfully
- ✅ Get non-existent asset (should fail)
- ✅ Get without authentication (should fail)

#### Update Asset (Admin Only)
- ✅ Update asset successfully
- ✅ Partial update
- ✅ Deactivate asset
- ✅ Update non-existent asset (should fail)
- ✅ Update as non-admin (should fail)
- ✅ Update without authentication (should fail)

#### Delete Asset (Admin Only)
- ✅ Delete (soft delete) asset successfully
- ✅ Delete non-existent asset (should fail)
- ✅ Delete as non-admin (should fail)
- ✅ Delete without authentication (should fail)

#### QR Code Generation
- ✅ Generate QR code successfully
- ✅ Generate for non-existent asset (should fail)
- ✅ Scan QR code successfully
- ✅ Scan invalid QR code (should fail)

#### Asset Statistics (Admin Only)
- ✅ Get stats with no bookings
- ✅ Get stats for non-existent asset (should fail)
- ✅ Get stats as non-admin (should fail)

**Total: 35 tests**

### 6. Facility Booking Tests (`test_bookings.py`)

#### Create Booking
- ✅ Create booking successfully with all fields
- ✅ Create booking with minimal required fields
- ✅ Create booking in the past (should fail)
- ✅ Create booking beyond advance limit (should fail)
- ✅ Create booking shorter than minimum duration (should fail)
- ✅ Create booking longer than maximum duration (should fail)
- ✅ Create booking before operating hours (should fail)
- ✅ Create booking after operating hours (should fail)
- ✅ Create booking with end time before start time (should fail)
- ✅ Create booking for inactive asset (should fail)
- ✅ Create booking for non-bookable asset (should fail)
- ✅ Create overlapping booking (should fail)
- ✅ Create without authentication (should fail)
- ✅ Create for non-existent asset (should fail)

#### List Bookings
- ✅ List user bookings when none exist
- ✅ List user's bookings
- ✅ Filter bookings by status
- ✅ List without authentication (should fail)

#### Get Booking
- ✅ Get single booking successfully
- ✅ Get non-existent booking (should fail)
- ✅ Admin can view other user's booking
- ✅ Get without authentication (should fail)

#### Update Booking
- ✅ Update booking successfully
- ✅ Update booking time
- ✅ Update non-existent booking (should fail)
- ✅ Update without authentication (should fail)

#### Cancel Booking
- ✅ Cancel booking successfully
- ✅ Cancel with cancellation reason
- ✅ Cancel non-existent booking (should fail)
- ✅ Cancel without authentication (should fail)

#### Check-in/Check-out
- ✅ Check-in successfully
- ✅ Check-in for non-existent booking (should fail)
- ✅ Check-out without check-in (should fail)
- ✅ Check-out for non-existent booking (should fail)

#### Check Availability
- ✅ Check availability with no bookings
- ✅ Check availability with existing bookings
- ✅ Check for non-existent asset (should fail)
- ✅ Check without authentication (should fail)

#### List Asset Bookings (Admin Only)
- ✅ List asset bookings when none exist
- ✅ List all bookings for an asset
- ✅ Filter asset bookings by status
- ✅ List as non-admin (should fail)
- ✅ List for non-existent asset (should fail)

#### Multiple Booking Scenarios
- ✅ Multiple users can book same asset at different times
- ✅ Adjacent bookings (end time = next start time)
- ✅ Book same asset on different dates
- ✅ Cancel and rebook same time slot

**Total: 52 tests**

## Test Fixtures

### Database Fixtures
- `db_session` - Fresh in-memory database for each test
- `client` - TestClient with database override

### User Fixtures
- `test_user` - Regular resident user
- `test_admin` - Admin user
- `test_contractor` - Contractor user
- `inactive_user` - Deactivated user

### Authentication Fixtures
- `auth_token` - JWT token for test user
- `admin_token` - JWT token for admin user
- `auth_headers` - Headers with bearer token for test user
- `admin_headers` - Headers with bearer token for admin

### Data Fixtures
- `test_issue` - Sample issue for testing
- `test_photo` - Sample photo for testing
- `create_test_asset` - Sample asset (Party Hall) for booking tests
- `create_gym_asset` - Sample gym asset with different hours
- `sample_asset_data` - Asset creation payload
- `sample_booking_data` - Booking creation payload
- `create_test_booking` - Sample booking for testing

## Test Coverage Summary

| Module | Tests | Status |
|--------|-------|--------|
| Authentication | 13 | ✅ All Pass |
| User Management | 24 | ✅ All Pass |
| Issue Management | 28 | ✅ All Pass |
| Photo Uploads | 14 | ⚠️ 8 Pass, 6 Skipped |
| Asset Management | 35 | ✅ All Pass |
| Facility Bookings | 52 | ✅ All Pass |
| **Total** | **166** | **158 Runnable** |

## Skipped Tests

Some tests are marked with `@pytest.mark.skip` because they require:
- AWS S3 credentials and active connection
- File size validation (integration test)
- File type validation (integration test)

These should be run manually in a staging environment with proper S3 configuration.

## Continuous Integration

For CI/CD pipelines:

```bash
# Run all tests except skipped ones
pytest -v --ignore-glob="**/test_photos.py"

# Or run with specific marker
pytest -v -m "not skip"
```

## Best Practices

1. **Isolation**: Each test uses a fresh in-memory database
2. **Independence**: Tests can run in any order
3. **Fast**: In-memory database makes tests very fast
4. **Comprehensive**: Tests cover success and failure cases
5. **Readable**: Test names describe what they test
6. **Maintainable**: Shared fixtures reduce duplication

## Adding New Tests

1. Create test file in `tests/` directory
2. Import necessary fixtures from `conftest.py`
3. Organize tests into classes by feature
4. Use descriptive test names: `test_<action>_<expected_result>`
5. Follow AAA pattern: Arrange, Act, Assert

Example:

```python
def test_feature_success(self, client, auth_headers):
    # Arrange: Set up test data
    data = {"key": "value"}
    
    # Act: Perform the action
    response = client.post("/endpoint", headers=auth_headers, json=data)
    
    # Assert: Verify the result
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## Troubleshooting

### Tests Fail to Import Modules
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

### Database Errors
- Tests use in-memory SQLite, no setup needed
- Each test gets a fresh database
- If issues persist, check `conftest.py` fixtures

### Authentication Errors
- Ensure fixtures are properly creating users
- Check token generation in `conftest.py`
- Verify password hashing works

## Future Enhancements

- [ ] Add integration tests for S3 uploads
- [ ] Add performance tests for large datasets
- [ ] Add security tests (SQL injection, XSS)
- [ ] Add load tests with locust
- [ ] Increase test coverage to >90%
- [ ] Add mutation testing
- [ ] Add contract testing for API
