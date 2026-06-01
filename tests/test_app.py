from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield


def test_get_activities_returns_all_activities() -> None:
    response = client.get("/activities")

    assert response.status_code == 200
    returned = response.json()
    assert isinstance(returned, dict)
    assert "Chess Club" in returned
    assert "Programming Class" in returned
    assert returned["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant() -> None:
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_bad_request() -> None:
    email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity() -> None:
    email = "daniel@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants?email=daniel%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed daniel@mergington.edu from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_not_found() -> None:
    response = client.delete(
        "/activities/Chess%20Club/participants?email=missing%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_missing_activity_returns_not_found() -> None:
    response = client.delete(
        "/activities/Unknown%20Club/participants?email=test%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
