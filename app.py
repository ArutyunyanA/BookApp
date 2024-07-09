import os
import json
from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)

# Генерация случайного секретного ключа
app.secret_key = os.urandom(24)

# Директория с книгами и путь к JSON файлу
BOOKS_DIRECTORY = os.path.join(os.getcwd(), 'static/books')
BOOKS_FILE = os.path.join(os.getcwd(), 'static/books.json')
USERNAME = 'admin'
PASSWORD = 'password'

def load_books():
    with open(BOOKS_FILE, 'r') as file:
        books = json.load(file)
    return books

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to be logged in to download books.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    books = load_books()
    return render_template('index.html', books=books)

@app.route('/download/<filename>')
@login_required
def download(filename):
    try:
        file_path = os.path.join(BOOKS_DIRECTORY, filename)
        return send_from_directory(BOOKS_DIRECTORY, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username  # Save the username in the session
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html', username=session.get('username', ''))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)