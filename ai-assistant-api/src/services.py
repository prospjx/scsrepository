import json
import logging
from typing import Any

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.schemas import (
    AIInsightsResponse,
    DiagnosticCheckInResponse,
    DiagnosticQuestion,
    ExtractedClass,
    ExtractScheduleResponse,
    FullLifeScheduleGenaiResponse,
    FullLifeScheduleResponse,
    RoutineBlock,
)

logger = logging.getLogger(__name__)


def _get_genai_client() -> genai.Client:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set or still has the placeholder value. "
            "Please add your actual Gemini API key to your .env file."
        )
    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(api_version="v1beta"),
    )


async def generate_ai_insights(
    student_profile: dict[str, Any], schedule: dict[str, Any]
) -> AIInsightsResponse:
    """
    Analyzes student profile and proposed schedule using Google Gemini,
    returning structured insights (summary, warnings, and suggestions).
    """
    try:
        client = _get_genai_client()

        prompt = f"""
You are an expert academic advisor AI. Analyze the following student profile and proposed course schedule.
Provide actionable, intelligent insights on workload balance, degree progression, prerequisite concerns, and study stress.

Student Profile:
{json.dumps(student_profile, indent=2)}

Proposed Schedule:
{json.dumps(schedule, indent=2)}

Provide your analysis strictly matching the requested JSON schema with:
- summary: A concise 1-2 sentence overview of how well-balanced or risky this schedule is.
- warnings: A list of potential concerns, pitfalls, or heavy workloads (empty list if none).
- suggestions: Concrete, actionable recommendations to improve or balance the schedule.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIInsightsResponse,
                temperature=0.2,
            ),
        )

        if response.text:
            parsed_data = json.loads(response.text)
            return AIInsightsResponse(**parsed_data)
        else:
            raise ValueError("Empty response received from Gemini model.")

    except ValueError as ve:
        logger.warning(f"Configuration / Validation error: {ve}")
        return AIInsightsResponse(
            summary="Schedule analysis is running in offline mode (API key not configured).",
            warnings=[str(ve)],
            suggestions=[
                "Set your GEMINI_API_KEY in the .env file to enable live AI insights."
            ],
        )
    except Exception as e:
        logger.exception("Error calling Gemini API")
        return AIInsightsResponse(
            summary="Unable to generate full AI insights at this time.",
            warnings=[f"AI Service Error: {e!s}"],
            suggestions=[
                "Please verify your Gemini API key and network connection, then try again."
            ],
        )


async def extract_schedule_from_image(
    image_bytes: bytes, mime_type: str = "image/png"
) -> ExtractScheduleResponse:
    """
    Extracts class schedule information from an uploaded timetable screenshot using Gemini multimodal vision.
    """
    try:
        client = _get_genai_client()

        prompt = """
You are an AI timetable and schedule parser. Carefully examine the provided image of a student's class schedule or timetable.
Extract all scheduled classes and sections.

For each class, extract:
- course_id: Course code/number (e.g., 'CS-3410', 'MATH-2310', 'CHEM-101')
- title: Name or title of the course (e.g., 'Computer Systems', 'Calculus I'). If not explicitly listed, use the course_id.
- day: Standardized day of the week ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
- start_time: 24-hour time format HH:MM (e.g. '09:00', '13:30', '10:00')
- end_time: 24-hour time format HH:MM (e.g. '10:15', '14:45', '11:15')
- location: Room or building name if visible, otherwise 'TBD' or 'Main Campus'.

Ensure multiple meetings of the same course on different days (e.g. Mon/Wed/Fri) are extracted as separate entries.
Return strictly the JSON matching the ExtractScheduleResponse schema.
"""

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractScheduleResponse,
                temperature=0.1,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            return ExtractScheduleResponse(**data)
        else:
            raise ValueError("No text response from Gemini vision model.")

    except Exception as e:
        logger.exception("Error extracting schedule from image")
        return ExtractScheduleResponse(
            success=False,
            message=f"Failed to extract schedule from image: {e!s}",
            extracted_classes=[],
        )


async def generate_diagnostic_check_in(
    student_profile: dict[str, Any], enrolled_classes: list[ExtractedClass]
) -> DiagnosticCheckInResponse:
    """
    Analyzes fixed classes and student profile, returning an empathetic observation
    and 2-3 targeted diagnostic questions before generating the routine.
    """
    try:
        client = _get_genai_client()

        prompt = f"""
You are an empathetic, insightful personal academic advisor AI.
The student has provided their enrolled class timetable and personal routine preferences.
Carefully inspect their weekly layout (identifying heavy back-to-back class days, awkward campus gaps, or light days).

Student Profile & Preferences:
{json.dumps(student_profile, indent=2)}

Enrolled Classes:
{json.dumps([c.model_dump() for c in enrolled_classes], indent=2)}

Task:
1. Provide a warm, brief, 1-2 sentence `greeting_observation` pointing out specific observations about their timetable (e.g., "I noticed your Tuesdays and Thursdays have back-to-back lectures, while Wednesdays give you a solid midday break.").
2. Generate 2 to 3 smart `questions` to calibrate their ideal weekly routine:
   - Question 1 (Coping & Fatigue): How they are coping with their heaviest class days and potential afternoon fatigue.
   - Question 2 (Study Priority): Which specific course from their timetable needs the most dedicated study focus right now.
   - Question 3 (Downtime/Commitments): Any preferred downtime, gym habit, or non-academic commitments they want guarded.
3. For each question, provide 3 realistic, distinct `quick_replies` (e.g., ["Drained by 3 PM", "Managing well", "Need light evenings"]).

Return strictly JSON matching DiagnosticCheckInResponse.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DiagnosticCheckInResponse,
                temperature=0.3,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            return DiagnosticCheckInResponse(**data)
        else:
            raise ValueError("No text response from Gemini model.")

    except Exception as e:
        logger.exception("Error generating diagnostic check-in")
        # Empathetic fallback
        course_names = [c.title or c.course_id for c in enrolled_classes[:2]]
        focus_example = course_names[0] if course_names else "Core Classes"
        return DiagnosticCheckInResponse(
            greeting_observation="I took a look at your course timetable and I'm ready to craft your ideal 7-day routine.",
            questions=[
                DiagnosticQuestion(
                    id="q1_fatigue",
                    question_text="How are you holding up with your busiest class days?",
                    quick_replies=["Exhausted after class", "Solid energy all day", "Need 1-hr break post-class"],
                ),
                DiagnosticQuestion(
                    id="q2_priority",
                    question_text=f"Which course needs the heaviest study focus right now?",
                    quick_replies=[f"Focus on {focus_example}", "Even split across all", "Prioritizing assignments"],
                ),
                DiagnosticQuestion(
                    id="q3_downtime",
                    question_text="What's your biggest priority for evening downtime?",
                    quick_replies=["Strict early bedtime", "Gym / workout session", "Relaxing / zero study after 8 PM"],
                ),
            ],
        )


async def generate_full_life_schedule(
    student_profile: dict[str, Any],
    enrolled_classes: list[ExtractedClass],
    diagnostic_answers: list[dict[str, Any]] | str | None = None,
) -> FullLifeScheduleResponse:
    """
    Synthesizes a complete daily and weekly life schedule integrating academic classes with:
    - Wake up and sleep routines
    - Transit to and from campus
    - Specific course study blocks
    - Gym / workout routines
    - Meals and personal time
    - Diagnostic check-in calibration
    """
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    prefs = student_profile.get("preferences", {})
    min_gap_commute = prefs.get("min_gap_for_commute_hours", 3)
    transit_mins = prefs.get("transit_time_minutes", 45)
    chronotype = prefs.get("energy_chronotype", "morning_lark")
    study_style = prefs.get("study_session_style", "deep_work")

    try:
        client = _get_genai_client()

        prompt = f"""
You are an elite student life and productivity planner AI.
Your goal is to build a complete, realistic, healthy 7-day routine schedule for a student that seamlessly integrates their enrolled academic classes with all their personal life preferences and diagnostic feedback.

Student Profile & Life Preferences:
{json.dumps(student_profile, indent=2)}

Enrolled Academic Classes (FIXED ANCHORS):
{json.dumps([c.model_dump() for c in enrolled_classes], indent=2)}

Student's Diagnostic Check-In Responses:
{json.dumps(diagnostic_answers, indent=2) if diagnostic_answers else "No extra diagnostic responses provided; use standard preferences."}

Scheduling Rules to Strictly Follow:
1. FIXED CLASSES: The student's academic classes MUST be placed at their exact scheduled day and times. Do not move them. Activity type = "Class".
2. WAKE UP & SLEEP:
   - Schedule wake up around `wake_up_time` ({prefs.get('wake_up_time', '07:00')}). Activity type = "Wakeup".
   - Schedule wind-down and sleep around `sleep_time` ({prefs.get('sleep_time', '23:00')}). Activity type = "Sleep".
3. SMART COMMUTE & CAMPUS GAPS:
   - On days with in-person classes, schedule "Transit to Campus" ({transit_mins} mins) before their first class.
   - Schedule "Transit Home" ({transit_mins} mins) after their last class.
   - DO NOT schedule "Transit Home" and "Transit to Campus" between two classes on the same day unless the gap between classes is at least {min_gap_commute} hours. For gaps shorter than {min_gap_commute} hours, keep the student on campus for lunch, a study session, or relaxation.
4. SPECIFIC COURSE STUDY BLOCKS (CRITICAL):
   - NEVER output generic study titles like "Morning Study", "Afternoon Study", or "Study Session".
   - ALWAYS name the specific course from their enrolled schedule, for example:
     * "Study: CS-3410 - Computer Systems"
     * "Deep Work: MATH-2310 - Linear Algebra"
     * "Review: CS-3500 - Software Engineering"
   - Distribute the student's target {prefs.get('study_hours_per_day', 3)} study hours per day across their actual enrolled subjects, weighting more study toward courses the student identified as challenging or high priority in their diagnostic answers.
5. COPING & BURNOUT AWARENESS:
   - If the student reported exhaustion or heavy fatigue on certain class days, schedule recovery, meals, or light review immediately after class, rather than intense study.
   - Align deep work sessions with their peak energy chronotype: '{chronotype}' ({'morning focus' if chronotype == 'morning_lark' else 'afternoon/evening peak' if chronotype == 'afternoon_peak' else 'late evening focus'}).
   - Structure study sessions according to '{study_style}' ({'45-60 min focused bursts' if study_style == 'pomodoro' else '90-120 min deep work blocks'}).
6. WORKOUT / GYM:
   - In accordance with `gym_time_preference` ('{prefs.get('gym_time_preference', 'afternoon')}') and `gym_duration_minutes` ({prefs.get('gym_duration_minutes', 60)} mins), place gym sessions on regular workout days without conflicting with classes or transit. Activity type = "Gym".
7. MEALS & DOWNTIME:
   - Include Lunch and Dinner / Relaxation breaks. Activity type = "Meal" or "Personal".
8. NO OVERLAPS: Ensure no activities overlap in time on any given day.
9. FORMAT: All times must be in 24-hour HH:MM format. Days must be one of: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.

Also generate comprehensive AI insights (summary, warnings, and suggestions) analyzing the balance, sleep health, and study pacing of this full routine.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FullLifeScheduleGenaiResponse,
                temperature=0.3,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            genai_resp = FullLifeScheduleGenaiResponse(**data)

            routine_map: dict[str, list[RoutineBlock]] = {d: [] for d in days}
            for day_obj in genai_resp.days:
                day_name = day_obj.day.capitalize()
                routine_map[day_name] = day_obj.activities

            return FullLifeScheduleResponse(
                weekly_routine=routine_map, ai_insights=genai_resp.ai_insights
            )
        else:
            raise ValueError("No text response from Gemini model.")

    except Exception as e:
        logger.exception("Error generating full life schedule")
        weekly_routine: dict[str, list[RoutineBlock]] = {d: [] for d in days}
        wake = prefs.get("wake_up_time", "07:00")
        sleep = prefs.get("sleep_time", "23:00")

        # Fallback study title using actual course if available
        first_course = enrolled_classes[0].title if enrolled_classes else "Academic Coursework"

        for c in enrolled_classes:
            day = c.day.capitalize()
            if day in weekly_routine:
                weekly_routine[day].append(
                    RoutineBlock(
                        day=day,
                        start_time=c.start_time,
                        end_time=c.end_time,
                        activity_type="Class",
                        title=f"{c.course_id} - {c.title}",
                        location=c.location,
                    )
                )

        # Basic fallback routine blocks
        for day in days:
            routine = weekly_routine[day]
            routine.insert(
                0,
                RoutineBlock(
                    day=day,
                    start_time=wake,
                    end_time="08:00",
                    activity_type="Wakeup",
                    title="Morning Routine & Breakfast",
                ),
            )
            routine.append(
                RoutineBlock(
                    day=day,
                    start_time="17:00",
                    end_time="18:30",
                    activity_type="Study",
                    title="Focused Study & Review",
                )
            )
            routine.append(
                RoutineBlock(
                    day=day,
                    start_time="19:00",
                    end_time="20:00",
                    activity_type="Gym",
                    title="Workout / Fitness",
                )
            )
            routine.append(
                RoutineBlock(
                    day=day,
                    start_time=sleep,
                    end_time="23:59",
                    activity_type="Sleep",
                    title="Night Sleep",
                )
            )

        return FullLifeScheduleResponse(
            weekly_routine=weekly_routine,
            ai_insights=AIInsightsResponse(
                summary="Full routine generated with fallback heuristics.",
                warnings=[f"AI note: {e!s}"],
                suggestions=[
                    "Ensure wake and sleep times are adhered to consistently."
                ],
            ),
        )
