'''
Main Application - FocusPad
'''
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape

# Init Flask app
app = Flask(__name__)

# Security config
app.secret_key = os.environ.get('SECRET_KEY', 'placeholderSecret')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,  # Prevents JS access to session cookie
    SESSION_COOKIE_SECURE=True,    # Makes sure cookies are sent through HTTPS only
    SESSION_COOKIE_SAMESITE='Lax'  # Stops cross-site cookie use
)

# Function to init SQLite db & tables
def init_db():
    with sqlite3.connect('notes.db') as conn:
        c = conn.cursor()
        # Table for user credentials
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # Table for user notes
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

# Init db tables
init_db()

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        user = escape(request.form['username'])
        password = request.form['password']

        # Validate usrname and password length
        if len(user) < 3 or len(password) < 4:
            error = "Username or password too short."
        else:
            # Hash the password
            pw = generate_password_hash(password)
            try:
                # Insert new user into db
                with sqlite3.connect('notes.db') as conn:
                    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
                return redirect('/login')
            except sqlite3.IntegrityError:
                error = "Username already exists. Please choose another."
    # Render registration page & potential error msg
    return render_template('register.html', error=error)

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = escape(request.form['username'])
        pw = request.form['password']
        with sqlite3.connect('notes.db') as conn:
            c = conn.cursor()
            # Get user credentials from db
            c.execute("SELECT id, password FROM users WHERE username = ?", (user,))
            result = c.fetchone()
            # Validate password and set session
            if result and check_password_hash(result[1], pw):
                session['user_id'] = result[0]
                return redirect('/dashboard')
            else:
                error = 'Invalid username or password.'
    # Render login page & potential error msg
    return render_template('login.html', error=error)

# Logout route clears session and redirects to homepage
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Dashboard route for creating and viewing notes
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    notes = []
    with sqlite3.connect('notes.db') as conn:
        c = conn.cursor()
        # New note submission
        if request.method == 'POST':
            title = escape(request.form['title'])
            content = escape(request.form['content'])
            if title and content:
                c.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
        # Get all user's notes
        c.execute("SELECT id, title, content FROM notes WHERE user_id = ?", (user_id,))
        notes = c.fetchall()
    # Render dashboard with user's notes
    return render_template('dashboard.html', notes=notes)

# Route to delete notes by ID
@app.route('/delete/<int:note_id>')
def delete(note_id):
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    # Delete the note if it belongs to the logged-in user
    with sqlite3.connect('notes.db') as conn:
        conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, session['user_id']))
    return redirect('/dashboard')

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
