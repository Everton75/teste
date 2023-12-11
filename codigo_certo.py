from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configuração do banco de dados SQLite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
conn.commit()

# Configuração do Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

# Classe de usuário


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Função para carregar o usuário


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1])
    return None

# Rota de login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            return redirect(url_for('logado'))

    return redirect(url_for('index'))

# Rota de logout


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rota protegida


@app.route('/logado')
@login_required
def logado():
    return render_template('logado.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
