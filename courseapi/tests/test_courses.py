def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_courses(client):
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) == 3
    course_ids = [c["course_id"] for c in courses]
    assert "CS-3410" in course_ids
    assert "CS-3500" in course_ids
    assert "MATH-2310" in course_ids


def test_get_course_details_success(client):
    response = client.get("/api/v1/courses/CS-3410")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == "CS-3410"
    assert data["title"] == "Computer Systems"
    assert data["credits"] == 4
    assert len(data["timeslots"]) == 2


def test_get_course_details_not_found(client):
    response = client.get("/api/v1/courses/NON_EXISTENT")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_create_new_course(client):
    new_course = {
        "course_id": "CS-4110",
        "title": "Distributed Systems",
        "credits": 3,
        "description": "Design and implementation of distributed systems.",
        "prerequisites": ["CS-3410"],
        "timeslots": [
            {
                "day": "Friday",
                "start_time": "14:00",
                "end_time": "16:00",
                "location": "Building D, Room 102",
            }
        ],
    }
    response = client.post("/api/v1/courses", json=new_course)
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == "CS-4110"
    assert data["title"] == "Distributed Systems"
    assert len(data["timeslots"]) == 1

    # Verify retrieval
    get_res = client.get("/api/v1/courses/CS-4110")
    assert get_res.status_code == 200
    assert get_res.json()["course_id"] == "CS-4110"


def test_update_existing_course(client):
    update_data = {
        "course_id": "CS-3410",
        "title": "Computer Systems - Updated",
        "credits": 4,
        "description": "Updated description",
        "prerequisites": ["CS-1110"],
        "timeslots": [
            {
                "day": "Monday",
                "start_time": "11:00",
                "end_time": "12:15",
                "location": "Building A, Room 202",
            }
        ],
    }
    response = client.post("/api/v1/courses", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Computer Systems - Updated"
    assert len(data["timeslots"]) == 1
    assert data["timeslots"][0]["start_time"] == "11:00"

    # Verify get details
    get_res = client.get("/api/v1/courses/CS-3410")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Computer Systems - Updated"
