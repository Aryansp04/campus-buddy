# Campus Buddy — Sylva Living Green Edition

**Campus Buddy** is an autonomous student AI copilot built for the AgentForge workshop, pairing a strict **ReAct (Reason → Act → Observe → Answer)** Python FastAPI + Groq (`openai/gpt-oss-120b`) backend with the exact **ThreeUI `<SylvaHero variant="living-green" />`** (`inner-green-3d.html`) 3D WebGL / WebGL2 living moss-root interface.

---

## Deploy on Vercel

This repository is pre-configured for **Vercel** (`api/index.py` + `vercel.json` + slim serverless `requirements.txt`):

1. Import **`Aryansp04/campus-buddy`** in [Vercel New Project](https://vercel.com/new).
2. Add the environment variable in **Project Settings → Environment Variables**:
   - `GROQ_API_KEY` = your Groq API key (`gsk_...`)
   - *(Optional)* `GROQ_MODEL` = `openai/gpt-oss-120b`
3. Click **Deploy** — Vercel serves `/landing-pages/inner-green-assets/*` from its global Edge CDN and routes `/` and `/api/*` through the FastAPI serverless function in `api/index.py`.

---

## Local Development

```powershell
pip install -r requirements.txt
# Copy .env.example to .env and add your GROQ_API_KEY
python server.py
```
Then open **[http://localhost:8501](http://localhost:8501)**.

### Run Tests
```powershell
python -m unittest discover -s tests -t . -v
```
