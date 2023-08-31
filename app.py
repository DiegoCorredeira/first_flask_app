import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from datetime import datetime

app = Flask(__name__)
app.secret_key = "\x128~\xb9\xaf\x88\xf2\x14\x88\xb1STcU\x04\xf66\xd9\xde@f\xb9'\x90"

def is_user_authenticated():
    return 'username' in session

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL,
          password TEXT NOT NULL
          )''')

conn.commit()
conn.close()


# criar uma rota para receber os dados do formulário
# Rota tem que ser com o mesmo nome da funcao (?) 
reservas = {}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if not is_user_authenticated():
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        servico = request.form['servico']
        data = request.form['data']
        hora = request.form['hora']



        if not nome or not servico or not data or not hora:
            return render_template('erro.html', mensagem='Todos os campos são obrigatórios. Por favor, tente novamente.')
        
        try:
            data_parse = datetime.strptime(data, '%Y-%m-%d')
            hora_parse = datetime.strptime(hora, '%H:%M').time()
        except ValueError:
            return render_template('erro.html', mensagem='Data inválida. Por favor, tente novamente.')
        
        if hora_parse.hour >= 18 or hora_parse.hour <= 9:
            return render_template('erro.html', mensagem='Horario de atendimento: 8h às 17h. Por favor, escolha outro horário.')

        dia_semana = data_parse.weekday()

        if dia_semana == 6:
            return render_template('erro.html', mensagem='Não atendemos aos domingos. Por favor, escolha outro dia.')

        if data in reservas and hora in reservas[data]:
            return render_template('erro.html', mensagem='Horário indisponível. Por favor, escolha outro horário.')

        if data not in reservas:
            reservas[data] = []
        reservas[data].append(hora)

        print('Novo agendamento:')
        print(f'Nome: {nome}')
        print(f'Serviço: {servico}')
        print(f'Data: {data}')
        print(f'Hora: {hora}')

        return render_template('confirmacao.html', nome=nome, servico=servico, data=data, hora=hora)

    return render_template('reservar.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['username'] = user[1]
            return redirect(url_for('reservar')) 
        else:
            flash('Credenciais inválidas', 'error')

    messages = get_flashed_messages()
    return render_template('login.html', messages=messages)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template('erro.html', mensagem='Todos os campos são obrigatórios. Por favor, tente novamente.')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            conn.close()
            flash('O nome de usuário já está em uso. Por favor, tente novamente.')
            return redirect(url_for('cadastro'))
        

        cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, password))

        conn.commit()
        conn.close()

        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)