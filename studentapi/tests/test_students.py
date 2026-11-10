from src.seed import DEFAULT_STUDENT_ID


def test_get_student_success(client, seed_student):
    """Test retrieving an existing student profile by student_id."""
    response = client.get(f"/api/v1/students/{DEFAULT_STUDENT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == DEFAULT_STUDENT_ID
    assert data["name"] == "Jane Doe"
    assert data["preferences"]["max_credits_per_term"] == 16
    assert data["preferences"]["difficulty_tolerance"] == "high"
    assert data["preferences"]["preferred_days_off"] == ["Monday", "Friday"]


def test_get_student_not_found(client):
    """Test retrieving a non-existent student returns 404."""
    response = client.get("/api/v1/students/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_update_student_success(client, seed_student):
    """Test updating an existing student profile."""
    payload = {
        "student_id": DEFAULT_STUDENT_ID,
        "name": "Jane Smith",
        "preferences": {
            "max_credits_per_term": 15,
            "preferred_days_off": ["Wednesday"],
            "difficulty_tolerance": "low",
            "preferred_time_of_day": "afternoon",
            "wake_up_time": "08:00",
            "sleep_time": "00:00",
            "study_hours_per_day": 2,
            "transit_time_minutes": 20,
            "gym_time_preference": "morning",
            "gym_duration_minutes": 50,
            "energy_chronotype": "night_owl",
            "study_session_style": "pomodoro",
            "min_gap_for_commute_hours": 4,
        },
    }
    response = client.put(f"/api/v1/students/{DEFAULT_STUDENT_ID}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["preferences"]["max_credits_per_term"] == 15
    assert data["preferences"]["preferred_days_off"] == ["Wednesday"]
    assert data["preferences"]["difficulty_tolerance"] == "low"
    assert data["preferences"]["energy_chronotype"] == "night_owl"
    assert data["preferences"]["study_session_style"] == "pomodoro"
    assert data["preferences"]["min_gap_for_commute_hours"] == 4

    # Verify persistence by fetching again
    fetch_resp = client.get(f"/api/v1/students/{DEFAULT_STUDENT_ID}")
    assert fetch_resp.status_code == 200
    assert fetch_resp.json()["name"] == "Jane Smith"
    assert fetch_resp.json()["preferences"]["energy_chronotype"] == "night_owl"


def test_update_student_not_found(client):
    """Test updating a non-existent student returns 404."""
    payload = {
        "student_id": "non-existent-id",
        "name": "Ghost Student",
        "preferences": {
            "max_credits_per_term": 12,
            "preferred_days_off": [],
            "difficulty_tolerance": "medium",
            "preferred_time_of_day": "any",
            "wake_up_time": "07:00",
            "sleep_time": "23:00",
            "study_hours_per_day": 3,
            "transit_time_minutes": 45,
            "gym_time_preference": "none",
            "gym_duration_minutes": 0,
        },
    }
    response = client.put("/api/v1/students/non-existent-id", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_update_student_validation_error(client, seed_student):
    """Test updating student with invalid schema returns 422 Unprocessable Entity."""
    invalid_payload = {
        "student_id": DEFAULT_STUDENT_ID,
        "name": "Jane Smith",
        # Missing preferences
    }
    response = client.put(
        f"/api/v1/students/{DEFAULT_STUDENT_ID}", json=invalid_payload
    )
    assert response.status_code == 422
