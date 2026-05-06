"""
Test suite for the Mergington High School Activities API.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Check that we have activities
        assert len(activities) > 0
        
        # Verify all required activities are present
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_has_correct_structure(self, client):
        """Verify that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_shows_initial_participants(self, client):
        """Verify that initial participants are loaded correctly."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, client):
        """Verify that a new participant can sign up for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_rejected(self, client):
        """Verify that duplicate signups are rejected."""
        # First signup succeeds
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_existing_participant_rejected(self, client):
        """Verify that students already signed up cannot sign up again."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Verify that signup fails for non-existent activities."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Verify that a student can sign up for multiple activities."""
        email = "multitalented@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant(self, client):
        """Verify that a participant can be unregistered from an activity."""
        # First, sign up a participant
        email = "toremove@mergington.edu"
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Verify that unregistering a non-participant fails."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Verify that unregister fails for non-existent activities."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_initial_participant(self, client):
        """Verify that initial participants can be unregistered."""
        # Michael is an initial participant in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]  # Other participant unaffected


class TestIntegrationScenarios:
    """Integration tests for realistic usage patterns."""

    def test_signup_and_unregister_flow(self, client):
        """Test the complete flow of signing up and then unregistering."""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Check initial state
        initial = client.get("/activities").json()
        initial_count = len(initial[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        after_signup = client.get("/activities").json()
        assert len(after_signup[activity]["participants"]) == initial_count + 1
        assert email in after_signup[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        after_unregister = client.get("/activities").json()
        assert len(after_unregister[activity]["participants"]) == initial_count
        assert email not in after_unregister[activity]["participants"]
    
    def test_multiple_operations_isolation(self, client):
        """Verify that operations on different activities don't interfere."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Sign up same student for two different activities
        client.post("/activities/Chess Club/signup", params={"email": email1})
        client.post("/activities/Art Club/signup", params={"email": email1})
        
        # Unregister from one activity
        client.delete("/activities/Chess Club/unregister", params={"email": email1})
        
        # Verify only removed from Chess Club
        activities = client.get("/activities").json()
        assert email1 not in activities["Chess Club"]["participants"]
        assert email1 in activities["Art Club"]["participants"]
