import io
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.main import app
from src.schemas import (
    AIInsightsResponse,
    ExtractScheduleResponse,
    FullLifeScheduleResponse,
)

client = TestClient(app)


def test_health_check():
    """Verify health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_schedule_success():
    """Test AI analyze schedule endpoint with mock response."""
    payload = {
        "student_profile": {
            "name": "Jane Doe",
            "major": "Computer Science",
            "preferences": {"wake_up_time": "08:00"},
        },
        "schedule": {
            "classes": [
                {
                    "course_id": "CS101",
                    "title": "Intro to CS",
                    "day": "Monday",
                    "start_time": "09:00",
                    "end_time": "10:30",
                }
            ]
        },
    }

    mock_insights = AIInsightsResponse(
        summary="Great balanced schedule.",
        warnings=[],
        suggestions=["Take a break after class."],
    )

    with patch(
        "src.routers.ai.generate_ai_insights", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.return_value = mock_insights
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Great balanced schedule."
        assert "Take a break after class." in data["suggestions"]


def test_extract_schedule_invalid_file_type():
    """Verify that uploading non-image file results in 400 Bad Request."""
    file_content = b"not an image content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/api/v1/analyze/extract-schedule", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_extract_schedule_empty_file():
    """Verify that uploading an empty image results in 400 Bad Request."""
    files = {"file": ("empty.png", io.BytesIO(b""), "image/png")}
    response = client.post("/api/v1/analyze/extract-schedule", files=files)
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]


def test_extract_schedule_success():
    """Verify schedule image extraction with mock."""
    mock_extracted = ExtractScheduleResponse(
        success=True,
        message="Schedule extracted successfully.",
        extracted_classes=[
            {
                "course_id": "MATH201",
                "title": "Linear Algebra",
                "day": "Monday",
                "start_time": "10:00",
                "end_time": "11:30",
                "location": "Hall A",
            }
        ],
    )

    with patch(
        "src.routers.ai.extract_schedule_from_image", new_callable=AsyncMock
    ) as mock_extract:
        mock_extract.return_value = mock_extracted
        fake_png = b"\x89PNG\r\n\x1a\nfakeimagebytes"
        files = {"file": ("schedule.png", io.BytesIO(fake_png), "image/png")}
        response = client.post("/api/v1/analyze/extract-schedule", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["extracted_classes"]) == 1
        assert data["extracted_classes"][0]["course_id"] == "MATH201"


def test_full_schedule_generation():
    """Verify full life routine generation endpoint."""
    payload = {
        "student_profile": {
            "name": "Jane Doe",
            "preferences": {
                "wake_up_time": "07:30",
                "sleep_time": "23:00",
            },
        },
        "enrolled_classes": [
            {
                "course_id": "CS101",
                "title": "Intro to CS",
                "day": "Monday",
                "start_time": "09:00",
                "end_time": "10:30",
                "location": "Room 101",
            }
        ],
        "diagnostic_answers": [
            {"question_id": "q1_fatigue", "answer": "Drained by 3 PM"}
        ],
    }

    mock_resp = FullLifeScheduleResponse(
        weekly_routine={
            "Monday": [
                {
                    "day": "Monday",
                    "start_time": "09:00",
                    "end_time": "10:30",
                    "activity_type": "Class",
                    "title": "CS101 - Intro to CS",
                }
            ]
        },
        ai_insights=AIInsightsResponse(
            summary="Routine generated.",
            warnings=[],
            suggestions=["Stick to consistent sleep schedule."],
        ),
    )

    with patch(
        "src.routers.ai.generate_full_life_schedule", new_callable=AsyncMock
    ) as mock_gen:
        mock_gen.return_value = mock_resp
        response = client.post("/api/v1/analyze/full-schedule", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "weekly_routine" in data
        assert "Monday" in data["weekly_routine"]
        assert "CS101" in data["weekly_routine"]["Monday"][0]["title"]


def test_diagnostic_check_in():
    """Verify diagnostic check-in endpoint returns empathetic observation and 2-3 questions."""
    from src.schemas import DiagnosticCheckInResponse, DiagnosticQuestion

    payload = {
        "student_profile": {
            "name": "Jane Doe",
            "preferences": {
                "energy_chronotype": "morning_lark",
                "study_session_style": "deep_work",
                "min_gap_for_commute_hours": 3,
            },
        },
        "enrolled_classes": [
            {
                "course_id": "CS-3410",
                "title": "Computer Systems",
                "day": "Tuesday",
                "start_time": "10:00",
                "end_time": "11:15",
                "location": "Hall A",
            }
        ],
    }

    mock_resp = DiagnosticCheckInResponse(
        greeting_observation="I noticed Tuesday mornings have a demanding lecture block.",
        questions=[
            DiagnosticQuestion(
                id="q1_fatigue",
                question_text="How are you coping with your Tuesday load?",
                quick_replies=["Managing fine", "Drained post-class", "Need an afternoon break"],
            )
        ],
    )

    with patch(
        "src.routers.ai.generate_diagnostic_check_in", new_callable=AsyncMock
    ) as mock_diag:
        mock_diag.return_value = mock_resp
        response = client.post("/api/v1/analyze/diagnostic-check-in", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "greeting_observation" in data
        assert len(data["questions"]) == 1
        assert data["questions"][0]["id"] == "q1_fatigue"
        assert len(data["questions"][0]["quick_replies"]) == 3

