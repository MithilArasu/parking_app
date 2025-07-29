import sqlite3
from flask import Flask, render_template, redirect, url_for, request, flash, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
DATABASE = app.config['DATABASE']

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.executescript(f.read())

# ---- Initialization block for Flask 2.3+ ----
with app.app_context():
    init_db()
    db = get_db()
    admin = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin:
        db.execute(
            'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
            ('admin', generate_password_hash('admin'), 1)
        )
        db.commit()
# ---------------------------------------------

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

from controllers.admin import admin_bp
from controllers.user import user_bp
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('user.user_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        existing = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        db.execute(
            'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), 0)
        )
        db.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
