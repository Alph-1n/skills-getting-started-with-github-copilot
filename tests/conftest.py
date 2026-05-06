"""
Pytest configuration and fixtures for API tests.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


# Store the original activities state at import time
ORIGINAL_ACTIVITIES = {
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
    "Soccer Team": {
        "description": "Practice soccer skills and compete in interschool matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "maria@mergington.edu"]
    },
    "Basketball Training": {
        "description": "Develop basketball techniques and teamwork on the court",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["toby@mergington.edu", "nina@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["lily@mergington.edu", "sam@mergington.edu"]
    },
    "Drama Workshop": {
        "description": "Practice acting, improvisation, and stage production",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["grace@mergington.edu", "leo@mergington.edu"]
    },
    "Debate Team": {
        "description": "Build public speaking and critical thinking skills",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["harper@mergington.edu", "noah@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for competitions",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
        "max_participants": 10,
        "participants": ["ava@mergington.edu", "isaac@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Provide a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database to its original state before each test.
    
    This fixture uses autouse=True to ensure all tests start with fresh data,
    preventing state pollution between tests.
    """
    # Import the app module to access its activities dictionary
    from src import app as app_module
    
    # Reset to original state before the test runs
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    
    yield
    
    # Cleanup after test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
