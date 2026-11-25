# Campus Buddy — Sylva Living Green Edition

**Campus Buddy** is an autonomous student AI copilot built for the AgentForge workshop, pairing a strict **ReAct (Reason → Act → Observe → Answer)** Python backend with the exact **ThreeUI `<SylvaHero variant="living-green" />`** (`inner-green-3d.html`) 3D WebGL / WebGL2 living moss-root interface.

---

## Highlights

- **Exact `<SylvaHero />` (`living-green`) Template & Shaders**:
  - Procedural 3D moss-covered arch roots (~190,000 instanced moss blades that part under your cursor), ferns, pale flower clusters, drifting pollen, cursor pollen trail, survey wireframe intro scan, and landing swallowtail butterfly.
  - Native 5-pass WebGL2 dispersion liquid-metal controls (`Ask Campus Buddy` pill & circular briefing play control).
  - Floating proximity-magnifying dock & specular pointer-tracking conic rims, configured with `Lexend` weight `300` (`headingSize: 63`, `bodySize: 16.5`, `headingLetterSpacing: -0.006`, `primaryColor: #ffffff`).
- **All 10 ThreeUI Registered Source Files & Binary Assets Preserved Byte-Exact**:
  - Canonical HTML & assets under `public/landing-pages/` and `public/landing-pages/inner-green-assets/`
  - Registered TypeScript & CSS modules under `src/shaders/`
- **Live Campus Buddy Data & ReAct Dashboard (`#dashboard`)**:
  - **Module 01 · ReAct Copilot**: Live tool-calling chat with expandable `Goal → Tool → Input → Observation` traces.
  - **Module 02 · Timetable Lookup**: Filterable semester schedule, rooms, buildings, and instructors (`data/timetable.json`).
  - **Module 03 · Calculator & 75% Tracker**: Attendance compliance margin calculator, AST-safe expression evaluator, and weighted SGPA calculator.
  - **Module 04 · Campus Directory**: Searchable campus services, library hours, Wi-Fi login, dining, medical 24/7, and shuttle bus schedules (`data/campus_info.json`).

---

## How to Run

### Start the Web Server (Port 8501)
```powershell
cd C:\Users\Aryan\.gemini\antigravity\scratch\campus_buddy
python server.py
```
Then open **[http://localhost:8501](http://localhost:8501)**.

### Run the Test Suite (Agent + SHA-256 Asset Verification + API)
```powershell
cd C:\Users\Aryan\.gemini\antigravity\scratch\campus_buddy
python -m unittest discover -s tests -t . -v
```
