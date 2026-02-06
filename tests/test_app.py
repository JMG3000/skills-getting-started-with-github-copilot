import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Basketball Team" in activities
        assert "Programming Class" in activities

    def test_activity_structure(self):
        """Test that activities have the required fields"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        email = "test@example.com"
        activity = "Chess Club"

        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]

    def test_signup_duplicate(self):
        """Test signup with duplicate email"""
        email = "duplicate@example.com"
        activity = "Chess Club"

        # First signup
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Duplicate signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_invalid_activity(self):
        """Test signup for non-existent activity"""
        email = "test@example.com"
        activity = "NonExistentActivity"

        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result


class TestUnregister:
    """Tests for unregister (delete) endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "testunreg@example.com"
        activity = "Basketball Team"

        # First signup
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Then unregister
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

    def test_unregister_not_signed_up(self):
        """Test unregister for email not signed up"""
        email = "notexist@example.com"
        activity = "Art Club"

        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result

    def test_unregister_invalid_activity(self):
        """Test unregister from non-existent activity"""
        email = "test@example.com"
        activity = "NonExistentActivity"

        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result


class TestRoot:
    """Tests for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
