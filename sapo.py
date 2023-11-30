from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import threading


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Conecta ao banco de dados
conn = sqlite3.connect('database.db')

# Cria um objeto de armazenamento local de threads para armazenar o cursor
thread_local_storage = threading.local()

# Rota de login


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


# Pagina inicial


@app.route('/')
def index():
    return 'Olá, usuário'


if __name__ == '__main__':
    app.run()
