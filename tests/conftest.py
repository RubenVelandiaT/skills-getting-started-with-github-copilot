"""
Pytest configuration and shared fixtures for backend API tests.
"""

import pytest
from starlette.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance with a fresh app state.
    This ensures test isolation by reinitializing the activities for each test.
    """
    # Arrange: Reset activities to initial state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and intramural play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater production, and performance workshops",
            "schedule": "Thursdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["william@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu"]
        },
        "Mathematics Club": {
            "description": "Advanced problem-solving and mathematical competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:45 PM",
            "max_participants": 20,
            "participants": ["andrew@mergington.edu", "jessica@mergington.edu"]
        }
    })
    
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Fixture providing a sample email for signup/unregister tests."""
    return "student@mergington.edu"


@pytest.fixture
def duplicate_email():
    """Fixture providing an email already signed up for Chess Club."""
    return "michael@mergington.edu"


@pytest.fixture
def full_activity():
    """Fixture providing an activity name that will be filled to capacity."""
    # Gym Class has max_participants=30 and 2 initial participants
    return "Gym Class"
