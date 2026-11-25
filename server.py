from dataclasses import asdict
from datetime import datetime
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agent.campus_agent import CampusBuddyAgent
from tools.calculator_tool import calculate_attendance, calculate_gpa, safe_calculate
from tools.search_tool import campus_search, load_campus_info
from tools.timetable_tool import load_timetable, lookup_timetable

CANONICAL_HTML_PATH = os.path.join(ROOT_DIR, "public", "landing-pages", "inner-green-3d.html")
DASHBOARD_FRAGMENT_PATH = os.path.join(ROOT_DIR, "public", "campus-buddy-fragment.html")
LANDING_PAGES_DIR = os.path.join(ROOT_DIR, "public", "landing-pages")

# Configured <SylvaHero /> props (SYLVA_TYPOGRAPHY recipe from pageRecipes.ts)
SYLVA_CONFIGURED_TYPOGRAPHY_CSS = """<style id="threeui-page-typography">
:root {
  --ink: #ffffff;
  --ink-soft: rgba(255, 255, 255, 0.62);
  --ink-faint: rgba(255, 255, 255, 0.44);
}
body { font-family: 'Lexend', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-weight: 300; }
.headline, .ghost {
  font-family: 'Lexend', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.headline {
  font-weight: 300;
  font-size: calc(63 * var(--u));
  line-height: calc(65 * var(--u));
  letter-spacing: -0.006em;
}
.lede {
  font-weight: 300;
  font-size: calc(16.5 * var(--u));
  line-height: calc(22 * var(--u));
}
@media (max-width: 900px) {
  .headline {
    font-size: calc(62 * var(--u));
    line-height: calc(66 * var(--u));
  }
  .lede {
    font-size: calc(19 * var(--u));
    line-height: calc(27 * var(--u));
  }
}
</style>"""


def _replace_exact(source: str, target: str, replacement: str) -> str:
    if target not in source:
        raise RuntimeError(f"Expected SylvaHero anchor not found: {target[:60]!r}")
    return source.replace(target, replacement, 1)


def build_campus_buddy_document() -> str:
    """
    Builds the Campus Buddy Dashboard directly from the byte-exact canonical
    public/landing-pages/inner-green-3d.html source, preserving 100% of its
    authored DOM structure, styling, shaders, Three.js moss-root world,
    landing butterfly, pollen, and WebGL2 liquid-metal controls while wiring
    all copy, cards, dock items, and dashboard modules to Campus Buddy's data.
    """
    with open(CANONICAL_HTML_PATH, "r", encoding="utf-8") as f:
        doc = f.read()

    with open(DASHBOARD_FRAGMENT_PATH, "r", encoding="utf-8") as f:
        fragment = f.read()

    # Split fragment into <style>, <section>, and <script> parts
    style_end = fragment.index("</style>") + len("</style>")
    script_start = fragment.index('<script id="campus-buddy-controller">')
    cb_styles = fragment[:style_end]
    cb_section = fragment[style_end:script_start].strip()
    cb_script = fragment[script_start:].strip()

    # 1. Resolve relative asset paths against /landing-pages/inner-green-assets/
    doc = doc.replace("inner-green-assets/", "/landing-pages/inner-green-assets/")

    # 2. Replace Sylva metadata & copy with Campus Buddy metadata & live hooks
    anchors = [
        (
            "<title>Sylva — Into the living world</title>",
            "<title>Campus Buddy — Student AI Copilot</title>",
        ),
        (
            '<meta name="description" content="Restoring wild places through patient design, native planting, and a deeper kind of stewardship.">',
            '<meta name="description" content="Campus Buddy — verified college timetable lookup, safe math & attendance calculator, and campus directory search.">',
        ),
        (
            'aria-label="Sylva — home"',
            'aria-label="Campus Buddy — home" data-cb-tab="hero"',
        ),
        (
            '<a class="dock-item is-active" data-dock data-spec data-burst href="#" style="--d:180ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><path d="M8 14V9"/><path d="M8 9c0-2.4 1.7-4.3 4-4.3.2 2.6-1.6 4.6-4 4.3Z"/><path d="M8 10.5C7.9 8.4 6.4 6.8 4.4 6.8 4.3 8.9 5.9 10.6 8 10.5Z"/></svg>\n'
            '        </span>\n'
            '        <span>Grove</span>\n'
            '      </a>',
            '<a class="dock-item is-active" data-dock data-spec data-burst data-cb-tab="assistant" href="#dashboard" style="--d:180ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><path d="M8 14V9"/><path d="M8 9c0-2.4 1.7-4.3 4-4.3.2 2.6-1.6 4.6-4 4.3Z"/><path d="M8 10.5C7.9 8.4 6.4 6.8 4.4 6.8 4.3 8.9 5.9 10.6 8 10.5Z"/></svg>\n'
            '        </span>\n'
            '        <span>Copilot</span>\n'
            '      </a>',
        ),
        (
            '<a class="dock-item" data-dock data-spec data-burst href="#" style="--d:230ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><path d="M1.6 12.4c2.4-3.4 4.3-5.1 5.7-5.1 2 0 3 3.6 5 3.6 1.1 0 1.9-.5 2.4-1.4"/><path d="M4.3 6.2C5.5 4.4 6.6 3.5 7.6 3.5c1.5 0 2.2 2.4 3.7 2.4"/></svg>\n'
            '        </span>\n'
            '        <span>Habitats</span>\n'
            '      </a>',
            '<a class="dock-item" data-dock data-spec data-burst data-cb-tab="timetable" href="#dashboard" style="--d:230ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><rect x="2.2" y="3.2" width="11.6" height="10.4" rx="2"/><path d="M2.2 6.4h11.6M5.4 2v2.4M10.6 2v2.4"/></svg>\n'
            '        </span>\n'
            '        <span>Timetable</span>\n'
            '      </a>',
        ),
        (
            '<a class="dock-item" data-dock data-spec data-burst href="#" style="--d:280ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><path d="M4 2.4h5.3L12 5.1v8.5H4z"/><path d="M9.2 2.4V5h2.7"/><path d="M6 8.4h4M6 10.8h2.8"/></svg>\n'
            '        </span>\n'
            '        <span>Journal</span>\n'
            '      </a>',
            '<a class="dock-item" data-dock data-spec data-burst data-cb-tab="calculator" href="#dashboard" style="--d:280ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><rect x="3" y="2" width="10" height="12" rx="2"/><path d="M5.5 5.2h5M5.5 8.5h1.5M9 8.5h1.5M5.5 11.2h1.5M9 11.2h1.5"/></svg>\n'
            '        </span>\n'
            '        <span>Calculator</span>\n'
            '      </a>',
        ),
        (
            '<a class="dock-item dock-item--enter" data-dock data-spec data-burst href="#" style="--d:330ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><path d="M6.6 2.5h5.1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6.6"/><path d="M2.6 8h6.6"/><path d="m7 5.6 2.4 2.4L7 10.4"/></svg>\n'
            '        </span>\n'
            '        <span>Enter</span>\n'
            '      </a>',
            '<a class="dock-item dock-item--enter" data-dock data-spec data-burst data-cb-tab="directory" href="#dashboard" style="--d:330ms">\n'
            '        <span class="glyph" aria-hidden="true">\n'
            '          <svg viewBox="0 0 16 16"><circle cx="7.2" cy="7.2" r="4.4"/><path d="m10.5 10.5 3.1 3.1"/></svg>\n'
            '        </span>\n'
            '        <span>Directory</span>\n'
            '      </a>',
        ),
        (
            '<div class="ghost fade" style="--d:1150ms" aria-hidden="true">SYLVA</div>',
            '<div class="ghost fade" style="--d:1150ms" aria-hidden="true">CAMPUS</div>',
        ),
        (
            '<p class="label">Our Ethos</p>\n      <h2>Let the wild lead.</h2>',
            '<p class="label" id="cb-hero-card1-label">Today\'s Timetable</p>\n      <h2 id="cb-hero-card1-title">CS101 · 09:00</h2>',
        ),
        (
            'aria-label="Read about Sylva"',
            'aria-label="Open class timetable"',
        ),
        (
            '<span><i style="--d:260ms">Step into</i></span>\n      <span><i style="--d:360ms">the living world</i></span>',
            '<span><i style="--d:260ms">Meet your</i></span>\n      <span><i style="--d:360ms">campus companion</i></span>',
        ),
        (
            '<p class="lede mask" style="--d:480ms; --pd:14; --pr:1">We restore wild places through patient design, native planting, and a deeper kind of stewardship.</p>',
            '<p class="lede mask" style="--d:480ms; --pd:14; --pr:1">Check class timetables, room locations, attendance math, and campus info — verified, never guessed.</p>',
        ),
        (
            '<span class="lbl">Explore the work</span>',
            '<span class="lbl">Ask Campus Buddy</span>',
        ),
        (
            'aria-label="Play the film"',
            'aria-label="Run today\'s schedule briefing"',
        ),
        (
            '<div><dt>Canopy restored</dt><dd>282 ha</dd></div>',
            '<div><dt id="cb-stat-a-dt">Class schedule</dt><dd id="cb-stat-a-dd">13 weekly</dd></div>',
        ),
        (
            '<div><dt>Native species</dt><dd>43 mapped</dd></div>',
            '<div><dt id="cb-stat-b-dt">Campus search</dt><dd id="cb-stat-b-dd">8 services</dd></div>',
        ),
        (
            '<p class="label">Field Note 07</p>\n      <h2>After the Rain</h2>',
            '<p class="label" id="cb-hero-card2-label">Attendance &amp; Math</p>\n      <h2 id="cb-hero-card2-title">75% Safe Rule</h2>',
        ),
        (
            'aria-label="Open field note: After the Rain"',
            'aria-label="Open attendance and math calculator"',
        ),
        (
            '<a class="scroll mask" style="--d:1040ms; --pd:9" href="#">Discover<span class="track"></span></a>',
            '<a class="scroll mask" style="--d:1040ms; --pd:9" href="#dashboard">Dashboard<span class="track"></span></a>',
        ),
    ]

    for target, replacement in anchors:
        doc = _replace_exact(doc, target, replacement)

    # 3. Inject configured <SylvaHero /> typography CSS + Dashboard styles in <head>
    doc = _replace_exact(doc, "</head>", f"{SYLVA_CONFIGURED_TYPOGRAPHY_CSS}\n{cb_styles}\n</head>")

    # 4. Place #dashboard right after </main> (before three.min.js & ready() so [data-spec] registers)
    doc = _replace_exact(doc, "</main>", f"</main>\n\n{cb_section}")

    # 5. Place Campus Buddy API & interaction controller right before </body>
    doc = _replace_exact(doc, "</body>", f"{cb_script}\n</body>")

    return doc


app = FastAPI(title="Campus Buddy — Sylva Living Green Edition")
agent = CampusBuddyAgent()

# Serve /landing-pages/* byte-for-byte from public/landing-pages/
app.mount("/landing-pages", StaticFiles(directory=LANDING_PAGES_DIR), name="landing-pages")


class ChatRequest(BaseModel):
    message: str


class AttendanceRequest(BaseModel):
    attended: int
    total: int
    target_percent: float = 75.0


class MathRequest(BaseModel):
    expression: str


class GpaCourse(BaseModel):
    name: str
    credits: float
    grade: Optional[str] = None
    grade_point: Optional[float] = None


class GpaRequest(BaseModel):
    courses: List[GpaCourse]


@app.get("/", response_class=HTMLResponse)
def serve_dashboard() -> HTMLResponse:
    return HTMLResponse(content=build_campus_buddy_document())


@app.get("/api/overview")
def api_overview() -> Dict[str, Any]:
    classes = load_timetable()
    services = load_campus_info()
    today_name = datetime.now().strftime("%A")
    today_classes = [c for c in classes if c.get("day", "").lower() == today_name.lower()]
    is_today = len(today_classes) > 0
    focus_day = today_name if is_today else "Monday"
    focus_classes = today_classes if is_today else [c for c in classes if c.get("day") == "Monday"]
    focus_classes.sort(key=lambda x: x.get("start_time", ""))

    return {
        "today": today_name,
        "is_today": is_today,
        "focus_day": focus_day,
        "focus_classes": focus_classes,
        "total_classes": len(classes),
        "total_services": len(services),
        "attendance_rule": "75%",
    }


@app.post("/api/chat")
def api_chat(req: ChatRequest) -> JSONResponse:
    try:
        out = agent.run(req.message)
        trace_dict = asdict(out["trace"]) if out.get("trace") else None
        return JSONResponse({"answer": out["answer"], "trace": trace_dict})
    except Exception:
        return JSONResponse({
            "answer": "Sorry! I ran into an issue checking that right now. Could you rephrase or give me a bit more detail?",
            "trace": None,
        })


@app.get("/api/timetable")
def api_timetable(
    query: Optional[str] = Query(default=None),
    day: Optional[str] = Query(default=None),
    course: Optional[str] = Query(default=None),
    instructor: Optional[str] = Query(default=None),
    room: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    try:
        return lookup_timetable(query=query, day=day, course=course, instructor=instructor, room=room)
    except Exception:
        return {"success": False, "count": 0, "classes": [], "message": "Could not load timetable right now."}


@app.post("/api/attendance")
def api_attendance(req: AttendanceRequest) -> Dict[str, Any]:
    try:
        return calculate_attendance(req.attended, req.total, req.target_percent)
    except Exception:
        return {"success": False, "error": "Please provide valid class numbers."}


@app.post("/api/calculate")
def api_calculate(req: MathRequest) -> Dict[str, Any]:
    try:
        return safe_calculate(req.expression)
    except Exception:
        return {"success": False, "error": "Invalid mathematical expression."}


@app.post("/api/gpa")
def api_gpa(req: GpaRequest) -> Dict[str, Any]:
    try:
        payload = [c.model_dump(exclude_none=True) for c in req.courses]
        return calculate_gpa(payload)
    except Exception:
        return {"success": False, "error": "Could not compute GPA. Please check course credits."}


@app.get("/api/search")
def api_search(
    query: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    try:
        if query and query.strip():
            res = campus_search(query)
            items = res.get("results", [])
        else:
            items = load_campus_info()

        if category and category.strip():
            cat_l = category.strip().lower()
            items = [d for d in items if d.get("category", "").lower() == cat_l]

        return {"success": True, "count": len(items), "results": items}
    except Exception:
        return {"success": False, "count": 0, "results": [], "message": "Campus directory unavailable."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8501)
