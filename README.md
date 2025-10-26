# FocusPad

Simple note-taking app with an HTML front-end and a Python back-end. FocusPad is focused on fast capture, distraction‑free editing, and easy export of notes.

## What / Why
What: A lightweight note app (HTML + Python).  
Why: Capture ideas quickly and retrieve them without friction.

## Quick start
1. Clone
   git clone https://github.com/m6lvink/FocusPad.git
   cd FocusPad

2. Create virtual env and install
   python3 -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt

3. Start dev server
   - If there is an app entrypoint (app.py / main.py):  
     python app.py
   - If it's a Flask app:  
     FLASK_APP=app.py flask run
   - If it's FastAPI:  
     uvicorn main:app --reload

4. Open http://localhost:8000 or the port printed by the server.

If you prefer Docker, add a Dockerfile and run:
   docker build -t focuspad .
   docker run -p 8000:8000 focuspad

## Features
- Fast note capture (keyboard-first workflow).
- HTML editor with minimal UI.
- Server-side note storage (Python).

## Tech
- Front-end: HTML, CSS, minimal JS
- Back-end: Python (framework TBD)
- Recommended dev tools: Black, isort, flake8 for Python; Prettier for HTML/CSS.

## Development notes
- Use Conventional Commits. Example: fix(api): handle 429 with jittered retries
- Keep commits focused and explain why, not only what.
- Run formatter before pushing:
  - python: black .
  - html/css: prettier --write "path/**/*.html"

## Contributing
- Create PRs from a feature branch.
- Describe the change and the motivation in the PR body.
- Link to a minimal reproducer for bugs.
- Keep PRs small and scoped.

## Known limitations
- Single-user, local-first design (no multi-user sync yet).
- No automated auth; credentials are not implemented.
- Performance for very large note collections (>1k notes) not tested.

