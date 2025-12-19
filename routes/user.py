from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/edit', methods=['GET'])
def edit_profile():
    mysql = current_app.config['mysql']
    user_id = session.get('user_id')

    cur = mysql.connection.cursor()
    cur.execute("SELECT username, photo FROM user WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()

    
    user = {"username": "", "photo": None}
    if row:
        # row[0] = username, row[1] = photo
        user["username"] = row[0]
        user["photo"] = row[1]

    return render_template('edit_profil.html', user=user)


@user_bp.route('/update', methods=['POST'])
def update_profile():
    mysql = current_app.config['mysql']
    user_id = session.get('user_id')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    photo_file = request.files.get('photo')

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # === Handle upload photo ===
    photo_nama = None
    if photo_file and photo_file.filename != "":
        filename = secure_filename(photo_file.filename)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
        photo_nama = filename

        upload_path = os.path.join(upload_folder, filename)
        try:
            photo_file.save(upload_path)
        except Exception as e:
            flash(f"Gagal menyimpan foto: {str(e)}", "danger")
            return redirect(url_for('user.edit_profile'))

        sql_photo = "UPDATE user SET photo=%s WHERE id=%s"
        cur = mysql.connection.cursor()
        cur.execute(sql_photo, (photo_nama, user_id))
        mysql.connection.commit()
        cur.close()

        session['photo'] = photo_nama  # simpan foto baru ke session

    # === Update username ===
    if username != "":
        sql_user = "UPDATE user SET username=%s WHERE id=%s"
        cur = mysql.connection.cursor()
        cur.execute(sql_user, (username, user_id))
        mysql.connection.commit()
        cur.close()

        session['username'] = username  # update session username juga jika digunakan

    # === Update password (jika diisi) ===
    if password and password.strip() != "":
        hashed_pw = generate_password_hash(password)
        sql_pw = "UPDATE user SET password=%s WHERE id=%s"
        cur = mysql.connection.cursor()
        cur.execute(sql_pw, (hashed_pw, user_id))
        mysql.connection.commit()
        cur.close()

    flash("Profil berhasil diperbarui", "success")
    return redirect(url_for('user.edit_profile'))
