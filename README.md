# FocusPad

Note-taking app with nature theme. Fast capture, clean interface, local storage.

## What / Why
What: Lightweight note app (HTML + Python + Flask).  
Why: Capture ideas quickly in a calm, distraction-free environment.

## Quick start

1. Clone and enter directory
   ```bash
   git clone https://github.com/m6lvink/FocusPad.git
   cd FocusPad
   ```

2. Set up environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create static folder
   ```bash
   mkdir -p static
   ```

4. Run application
   ```bash
   python app.py
   ```

5. Open http://localhost:5000

## Features

- User registration and login
- Create, view, delete notes
- Nature-inspired design
- Light and dark themes
- SQLite storage
- Fast and lightweight

## Design

- Earth tone colors (forest green, sage, moss)
- Sand and bark backgrounds
- Clean typography
- Minimal animations
- 8px border radius
- Left border accents on cards

## File structure

```
FocusPad/
├── app.py              # Flask application
├── notes.db            # SQLite database
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css      # Nature theme styles
└── templates/
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── login.html     # Login form
    ├── register.html  # Registration form
    └── dashboard.html # Note dashboard
```

## Tech stack

- Backend: Flask + SQLite
- Frontend: HTML, CSS, minimal JavaScript
- Design: Nature theme with earth tones
- No external CSS frameworks

## Development

Format code before committing:
```bash
black .
prettier --write "templates/**/*.html"
```

Use conventional commits:
```bash
git commit -m "feat(ui): add note search"
git commit -m "fix(auth): validate password length"
```

## Security

- Passwords hashed with Werkzeug
- Session cookies HTTP-only
- CSRF protection via Flask session
- Input sanitized with escape()
- Set SECRET_KEY environment variable in production

## Customization

Edit CSS variables in `static/style.css`:
```css
--forest: #2d5016;
--sage: #6b8e23;
--earth: #8b7355;
```

## Known limitations

- Single user per instance
- Local storage only
- Not tested with more than 1000 notes
- No search functionality yet
- No export functionality yet

## Contributing

- Create PRs from a feature branch
- Describe the change and motivation in PR body
- Keep PRs small and focused
- Link to issues when applicable

## License

MIT