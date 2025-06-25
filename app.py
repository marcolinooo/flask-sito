import datetime
from datetime import datetime
from flask import Flask, flash, redirect, render_template,request, session, url_for
from forms import ContattoForm, LoginForm,PrenotazioneForm, RegisterForm
import mysql.connector
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chiave segreta per sessioni e CSRF (meglio caricarla da variabile ambiente in produzione)

def get_db_connection():
    return mysql.connector.connect(
        host="mysql.railway.internal",
        user="root",
        password="AsLLHeojpOxoIDSiScBqQWeMxbGtYlzu",
        database="railway"
    )

@app.route("/")
def home():
    user_logged_in = 'user_id' in session
    username = session.get('username', None)
    return render_template('home.html', user_logged_in=user_logged_in, username=username)

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/chisiamo")
def chisiamo():
    return render_template("chisiamo.html")

@app.route('/contatti', methods=['GET', 'POST'])
def contatti():
    form = ContattoForm()
    success = False

    if form.validate_on_submit():
        # salva il messaggio come già fai
        with open('messaggi.txt', 'a', encoding='utf-8') as f:
            f.write(f"Nome: {form.nome.data}\n")
            f.write(f"Email: {form.email.data}\n")
            f.write(f"Telefono: {form.telefono.data}\n")
            f.write(f"Messaggio: {form.messaggio.data}\n")
            f.write("------\n")
        
        success = True
        form = ContattoForm()  # resetta form per evitare doppio invio

    return render_template('contatti.html', form=form, success=success)


@app.route('/prenotazione', methods=['GET', 'POST'])
def prenotazione():
    form = PrenotazioneForm()

    if form.validate_on_submit():
        nome = form.nome.data
        data = form.data.data
        ora = form.orario.data
        persone = form.persone.data
        email = form.email.data
        telefono = form.telefono.data
        note = form.note.data  # se presente nel form

        # Connessione e inserimento nel DB
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO prenotazioni (nome, data, ora, persone, email, telefono, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome, data, ora, persone, email, telefono, note))
        conn.commit()

        cursor.close()
        conn.close()

        return render_template('grazie.html',
                               nome=nome,
                               data=data,
                               ora=ora,
                               persone=persone)

    return render_template('prenotazione.html', form=form)

from flask import request, session, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash
from forms import LoginForm  # importa la tua classe LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM utenti WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                flash('Accesso come admin effettuato con successo', 'success')
                return redirect(url_for('admin'))
            else:
                flash(f'Iscrizione avvenuta con successo. Benvenuto, {user["username"]}', 'success')
                return redirect(url_for('home'))
        else:
            flash('Credenziali non valide', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Hash della password con metodo valido
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se l'utente o l'email esistono già
        cursor.execute("SELECT * FROM utenti WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username o email già registrati.', 'danger')
            cursor.close()
            conn.close()
            return render_template('register.html', form=form)

        # Inserisci nuovo utente con ruolo "user"
        cursor.execute(
            "INSERT INTO utenti (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, 'user')
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registrazione avvenuta con successo! Ora effettua il login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)




@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('Accesso negato.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM prenotazioni ORDER BY data DESC, ora ASC")
    prenotazioni = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin.html', prenotazioni=prenotazioni)

@app.route('/admin/modifica/<int:id>', methods=['POST'])
def modifica_prenotazione(id):
    nome = request.form['nome']
    email = request.form['email']
    data = request.form['data']
    ora = request.form['ora']
    persone = request.form['persone']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE prenotazioni SET nome=%s, email=%s, data=%s, ora=%s, persone=%s WHERE id=%s
    """, (nome, email, data, ora, persone, id))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Prenotazione modificata.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/elimina/<int:id>')
def elimina_prenotazione(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prenotazioni WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Prenotazione eliminata.', 'danger')
    return redirect(url_for('admin'))

@app.route('/admin/aggiungi', methods=['POST'])
def aggiungi_prenotazione():
    nome = request.form['nome']
    email = request.form['email']
    data = request.form['data']
    ora = request.form['ora']
    persone = request.form['persone']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO prenotazioni (nome, email, data, ora, persone)
        VALUES (%s, %s, %s, %s, %s)
    """, (nome, email, data, ora, persone))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Prenotazione aggiunta.', 'success')
    return redirect(url_for('admin'))

@app.context_processor
def inject_now():
    return {'now': datetime.now}
    
if __name__ == "__main__":
    app.run(debug=True)