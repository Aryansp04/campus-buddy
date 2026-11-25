import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "timetable.json")

def load_timetable() -> List[Dict[str, Any]]:
    """Loads timetable data safely."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def lookup_timetable(
    query: Optional[str] = None,
    day: Optional[str] = None,
    course: Optional[str] = None,
    instructor: Optional[str] = None,
    room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search and retrieve class timetable details.
    
    Args:
        query: Free-text search string (e.g., 'CS101', 'Monday', 'Dr. Feynman')
        day: Day of week (e.g., 'Monday', 'Tuesday', etc. or 'today')
        course: Course code or name (e.g., 'CS101', 'Physics')
        instructor: Faculty member's name
        room: Room or Hall number
        
    Returns:
        Structured result dictionary with status, count, and readable summary.
    """
    entries = load_timetable()
    if not entries:
        return {
            "success": False,
            "count": 0,
            "classes": [],
            "message": "Timetable database is currently unavailable or empty."
        }

    # Handle 'today' or 'tomorrow'
    if day:
        day_lower = day.strip().lower()
        if day_lower == "today":
            day = datetime.now().strftime("%A")
        elif day_lower == "tomorrow":
            # rough day shift
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_idx = datetime.now().weekday()
            day = weekdays[(current_idx + 1) % 7]

    matched = []
    
    # Normalize query term if provided as a single string
    q = (query or "").strip().lower()
    d = (day or "").strip().lower()
    c = (course or "").strip().lower()
    inst = (instructor or "").strip().lower()
    r = (room or "").strip().lower()

    for item in entries:
        item_day = item.get("day", "").lower()
        item_code = item.get("course_code", "").lower()
        item_name = item.get("course_name", "").lower()
        item_inst = item.get("instructor", "").lower()
        item_room = item.get("room", "").lower()
        item_bldg = item.get("building", "").lower()

        # Specific filters
        if d and d not in item_day:
            continue
        if c and (c not in item_code and c not in item_name):
            continue
        if inst and inst not in item_inst:
            continue
        if r and (r not in item_room and r not in item_bldg):
            continue

        # General free-text query check
        if q:
            match_any = (
                q in item_day or
                q in item_code or
                q in item_name or
                q in item_inst or
                q in item_room or
                q in item_bldg
            )
            if not match_any:
                continue

        matched.append(item)

    # Sort matched classes by day of week and time
    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
    matched.sort(key=lambda x: (day_order.get(x.get("day", ""), 99), x.get("start_time", "")))

    if not matched:
        filters = []
        if day: filters.append(f"Day: '{day}'")
        if course: filters.append(f"Course: '{course}'")
        if instructor: filters.append(f"Instructor: '{instructor}'")
        if room: filters.append(f"Room: '{room}'")
        if query: filters.append(f"Query: '{query}'")
        criteria = ", ".join(filters) if filters else "specified criteria"
        return {
            "success": True,
            "count": 0,
            "classes": [],
            "message": f"No scheduled classes found matching {criteria}."
        }

    # Format human-friendly schedule summary
    formatted_lines = []
    for item in matched:
        formatted_lines.append(
            f"📅 {item['day']} | ⏰ {item['start_time']} - {item['end_time']} | "
            f"📘 {item['course_code']}: {item['course_name']} | "
            f"📍 {item['room']} ({item['building']}) | 👨‍🏫 {item['instructor']} ({item['credits']} credits)"
        )

    return {
        "success": True,
        "count": len(matched),
        "classes": matched,
        "summary": "\n".join(formatted_lines),
        "message": f"Found {len(matched)} matching class(es)."
    }
