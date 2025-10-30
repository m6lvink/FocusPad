''' 
Main Application - FocusPad (with CSRF, CSP, and static MIME fix)
'''
import mimetypes  # ensure CSS served w/ text/css MIME type
mimetypes.add_type('text/css', '.css')

from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
import secrets

# Init Flask app
app = Flask(__name__)

# Security config
app.secret_key = os.environ.get('SECRET_KEY', 'placeholderSecret')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', '0') == '1',
)

# Implemented CSRF protection for all write operations
csrf = CSRFProtect(app)

# Database setup
def init_db():
    with sqlite3.connect('notes.db') as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

@app.before_request
def before_request():
    init_db()

# Generated a per-request nonce for CSP
@app.before_request
def before_request():
    g.csp_nonce = secrets.token_urlsafe(16)

# Exposed CSP nonce to templates
@app.context_processor
def inject_csp_nonce():
    return {'csp_nonce': getattr(g, 'csp_nonce', '')}

# Set strict security headers and CSP for safer defaults
@app.after_request
def set_security_headers(response):
    csp = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{getattr(g, 'csp_nonce', '')}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    if os.environ.get('ENABLE_HSTS', '0') == '1':
        response.headers['Strict-Transport-Security'] = 'max-age=15552000; includeSubDomains; preload'
    return response

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('register.html', error='Username and password are required')
        pw_hash = generate_password_hash(password)
        try:
            with sqlite3.connect('notes.db') as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pw_hash))
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        with sqlite3.connect('notes.db') as conn:
            cur = conn.execute("SELECT id, password FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
        if not row or not check_password_hash(row[1], password):
            return render_template('login.html', error='Invalid username or password')
        session.clear()
        session['user_id'] = row[0]
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if title and content:
            with sqlite3.connect('notes.db') as conn:
                conn.execute("INSERT INTO notes (title, content, user_id) VALUES (?, ?, ?)", (title, content, session['user_id']))
        return redirect(url_for('dashboard'))
    with sqlite3.connect('notes.db') as conn:
        cur = conn.execute("SELECT id, title, content FROM notes WHERE user_id = ?", (session['user_id'],))
        notes = cur.fetchall()
    return render_template('dashboard.html', notes=notes)

# Switched to POST and added CSRF for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# Switched to POST and added CSRF for deleting notes
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('notes.db') as conn:
        conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, session['user_id']))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
