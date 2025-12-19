from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']

        mysql = current_app.config['mysql']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, password, photo FROM user WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            user_id_db, username_db, password_db, photo_db = user

            
            valid = check_password_hash(password_db, pw)

            if valid:
                session['user_id'] = user_id_db
                session['username'] = username_db
                session['photo'] = photo_db
                flash("Login berhasil", "success")
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash("Username atau Password salah.", "error")
                return redirect(url_for('auth.login'))

        flash("Username atau Password salah.", "error")
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    theme = session.get('theme')
    session.clear()
    if theme:
        session['theme'] = theme
    return redirect(url_for('auth.login'))
