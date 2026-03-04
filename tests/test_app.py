"""
Test suite for Mergington High School API

Tests cover all endpoints using the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient connected to the FastAPI app.
    This client is used to make HTTP requests in tests.
    """
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns a list of all activities with correct structure"""
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify each activity has the expected structure
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert set(activity_data.keys()) == expected_keys
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_to_nonexistent_activity(self, client):
        """Test signup fails when activity does not exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_email(self, client):
        """Test signup fails when student is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in initial data

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister fails when activity does not exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_when_not_registered(self, client):
        """Test unregister fails when student is not signed up for activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "notregistered@mergington.edu"  # Not in participants

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Arrange - no setup needed for redirect test

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
