from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secret-key'

# Initialize DB
def init_db():
    with sqlite3.connect('notes.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        pw = generate_password_hash(request.form['password'])
        try:
            with sqlite3.connect('notes.db') as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
            return redirect('/login')
        except sqlite3.IntegrityError:
            error = "Username already exists. Please choose another."
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        with sqlite3.connect('notes.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, password FROM users WHERE username = ?", (user,))
            result = c.fetchone()
            if result and check_password_hash(result[1], pw):
                session['user_id'] = result[0]
                return redirect('/dashboard')
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    with sqlite3.connect('notes.db') as conn:
        c = conn.cursor()
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            c.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
        c.execute("SELECT id, title, content FROM notes WHERE user_id = ?", (user_id,))
        notes = c.fetchall()
    return render_template('dashboard.html', notes=notes)

@app.route('/delete/<int:note_id>')
def delete(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('notes.db') as conn:
        conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, session['user_id']))
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
