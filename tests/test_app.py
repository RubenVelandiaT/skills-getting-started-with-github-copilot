"""
Backend API tests for the Mergington High School extracurricular activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the endpoint request
- Assert: Verify response status, body, and side effects
"""

import pytest
from starlette.testclient import TestClient


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static_index_html(self, client):
        """
        Arrange: Initialize TestClient
        Act: GET /
        Assert: Returns 307 redirect to /static/index.html
        """
        # Arrange
        # (setup via client fixture)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Initialize TestClient with 9 activities in database
        Act: GET /activities
        Assert: Returns 200 with all 9 activities and correct structure
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Mathematics Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert set(activities_data.keys()) == set(expected_activities)

        # Verify structure of each activity
        for activity_name, activity_data in activities_data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_succeeds(self, client, sample_email):
        """
        Arrange: Initialize with a new student email not signed up for any activity
        Act: POST /activities/Chess Club/signup?email=student@mergington.edu
        Assert: Returns 200, student added to participants list
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {sample_email} for {activity_name}"

        # Verify student was added to participants
        activities = client.get("/activities").json()
        assert sample_email in activities[activity_name]["participants"]

    def test_signup_invalid_activity_returns_404(self, client, sample_email):
        """
        Arrange: Initialize with a non-existent activity name
        Act: POST /activities/Nonexistent Club/signup?email=student@mergington.edu
        Assert: Returns 404 with error detail
        """
        # Arrange
        activity_name = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client, duplicate_email):
        """
        Arrange: Student already signed up for Chess Club (michael@mergington.edu)
        Act: POST /activities/Chess Club/signup?email=michael@mergington.edu
        Assert: Returns 400 with error detail
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_to_full_activity_returns_400(self, client):
        """
        Arrange: Fill an activity to max capacity, then attempt to sign up new student
        Act: POST to full activity with new student email
        Assert: Returns 400 with error detail (only if activity is actually full)
        
        Note: Since activities must be filled to capacity, we find/fill an activity
        or skip if none are small enough to fill in a test.
        """
        # Arrange: Find an activity with small max_participants to fill
        # Art Studio has max_participants=18 with 1 initial participant
        activities = client.get("/activities").json()
        activity_name = "Art Studio"
        activity = activities[activity_name]
        max_participants = activity["max_participants"]
        current_participants = len(activity["participants"])

        # Fill the activity to max capacity
        for i in range(current_participants, max_participants):
            email = f"filler{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Act: Try to sign up one more student when activity is full
        new_student_email = "overflow@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower() or \
               "max" in response.json()["detail"].lower() or \
               "participants" in response.json()["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_student_succeeds(self, client, duplicate_email):
        """
        Arrange: Student is signed up for Chess Club (michael@mergington.edu)
        Act: DELETE /activities/Chess Club/unregister?email=michael@mergington.edu
        Assert: Returns 200, student removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": duplicate_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {duplicate_email} from {activity_name}"

        # Verify student was removed from participants
        activities = client.get("/activities").json()
        assert duplicate_email not in activities[activity_name]["participants"]

    def test_unregister_from_invalid_activity_returns_404(self, client, duplicate_email):
        """
        Arrange: Initialize with a non-existent activity name
        Act: DELETE /activities/Nonexistent Club/unregister?email=student@email.com
        Assert: Returns 404 with error detail
        """
        # Arrange
        activity_name = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": duplicate_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_in_activity_returns_400(self, client, sample_email):
        """
        Arrange: Student not signed up for Chess Club (new student email)
        Act: DELETE /activities/Chess Club/unregister?email=student@mergington.edu
        Assert: Returns 400 with error detail
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"
