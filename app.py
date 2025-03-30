from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar flash messages

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb+srv://fagalmeida:1234@cluster0.xm9sz.mongodb.net/meu_banco?retryWrites=true&w=majority"

mongo = PyMongo(app)

# Página inicial
@app.route('/')
def home():
    return render_template('home.html')

# Página inicial (página de "INÍCIO")
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

# Página de login
@app.route('/login', methods=['GET', 'POST'])  # Corrigido: adicionado @
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Tentando login com usuário: {username}")

        try:
            # Corrigido: usando mongo.db em vez de db
            user = mongo.db.usuarios.find_one({'username': username})
            if not user:
                flash("Usuário não encontrado", 'error')
                return render_template('login.html')

            print(f"Usuário encontrado: {user}")

            if check_password_hash(user.get('password', ''), password):
                flash("Login bem-sucedido", 'success')
                return redirect(url_for('inicio'))
            else:
                flash("Usuário ou senha inválidos", 'error')
                return render_template('login.html')

        except Exception as e:
            print(f"Erro no login: {str(e)}")
            flash(f"Erro ao acessar o banco de dados: {str(e)}", 'error')
            return render_template('login.html')

    return render_template('login.html')

# Página de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return "As senhas não coincidem. Tente novamente.", 400
        
        try:
            if mongo.db.usuarios.find_one({'username': username}):
                return "Usuário já existe. Tente outro nome.", 400

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            mongo.db.usuarios.insert_one({'username': username, 'email': email, 'password': hashed_password})
        
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Erro ao registrar o usuário: {str(e)}")
            return f"Erro ao acessar o banco de dados: {str(e)}", 500

    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)