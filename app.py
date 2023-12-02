from flask import Flask, render_template, redirect, url_for, request, Blueprint,  jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import threading


# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'sua_chave_secreta'

# Configuração do banco de dados SQLite3
conn = sqlite3.connect('database.db')

# Cria um objeto de armazenamento local de threads para armazenar o cursor
thread_local_storage = threading.local()

cursor = conn.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
conn.commit()

# Configuração do Flask Login
login_manager = LoginManager()
login_manager.init_app(app)


# Registro do Blueprint para servir arquivos estáticos
app.register_blueprint(
    Blueprint('static', __name__, static_folder='static', static_url_path='/static'))

# Classe de usuário


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            return User(user[0])
        return None

# Função para carregar o usuário


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Rota de login


@app.route('/login_re', methods=['GET', 'POST'])
def login_re():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            user_obj = User(user[0])
            login_user(user_obj)
            return redirect(url_for('adm'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])

def login():
    # Pega o objeto cursor do armazenamento local de threads
    cursor = thread_local_storage.cursor

    # Se o objeto cursor não existir, crie um novo
    if cursor is None:
        cursor = conn.cursor()
        thread_local_storage.cursor = cursor

    # Use o objeto cursor para executar sua consulta SQL
    username = request.form['username']
    password = request.form['password']
    cursor.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rota protegida


@app.route('/adm')
@login_required
def adm():
    return 'Olá, usuário Administrador!'


# pagina inicial
@app.route('/')
def index():
    return 'Olá, usuário '

@app.route("/users", methods=["GET"])
def get_users():
    # Abre uma conexão ao banco de dados
    conn = sqlite3.connect("database.db")

    # Cria uma consulta para selecionar todos os usuários
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    # Obtém os resultados da consulta
    users = cursor.fetchall()

    # Fecha a conexão ao banco de dados
    conn.close()

    # Converte os resultados em um objeto JSON
    users = [
        {
            "id": row[0],
            "username": row[1],
            "password": row[2]
        }
        for row in users
    ]

    return jsonify(users)


if __name__ == '__main__':
    app.run()
