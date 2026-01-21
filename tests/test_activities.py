"""Tests for the FastAPI activities API."""
import pytest


def test_root_redirect(client):
    """Test that root endpoint redirects to static page."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) == 9
    
    # Verify Chess Club is in activities
    assert "Chess Club" in activities
    assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert activities["Chess Club"]["max_participants"] == 12
    assert len(activities["Chess Club"]["participants"]) == 2


def test_get_activities_structure(client):
    """Test that activities have correct structure."""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for the signup endpoint."""
    
    def test_signup_successful(self, client):
        """Test successfully signing up for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity."""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signing up when already registered."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_activities(self, client):
        """Test signing up for multiple different activities."""
        email = "multistudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the unregister endpoint."""
    
    def test_unregister_successful(self, client):
        """Test successfully unregistering from an activity."""
        email = "michael@mergington.edu"
        
        # Verify participant is registered
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity."""
        response = client.post(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not registered for this activity"
    
    def test_signup_then_unregister(self, client):
        """Test signing up then unregistering from an activity."""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Soccer Team/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Soccer Team"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/Soccer Team/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Soccer Team"]["participants"]


class TestActivityAvailability:
    """Tests for checking activity availability."""
    
    def test_participant_count(self, client):
        """Test that participant counts are correct."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        
        # Programming Class should have 2 participants
        assert len(activities["Programming Class"]["participants"]) == 2
    
    def test_spots_available(self, client):
        """Test calculating available spots."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club: 12 max, 2 participants = 10 spots left
        chess_spots = activities["Chess Club"]["max_participants"] - len(activities["Chess Club"]["participants"])
        assert chess_spots == 10
        
        # Gym Class: 30 max, 2 participants = 28 spots left
        gym_spots = activities["Gym Class"]["max_participants"] - len(activities["Gym Class"]["participants"])
        assert gym_spots == 28
