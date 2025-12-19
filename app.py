from flask import Flask, redirect, url_for, session
from flask_mysqldb import MySQL
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.sertifikasi import sertifikasi_bp
from routes.user import user_bp

app = Flask(__name__)
app.secret_key = 'secretkey'

# Config DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_aplikasi'

mysql = MySQL(app)
app.config['mysql'] = mysql

@app.context_processor
def inject_theme():
    return dict(theme=session.get('theme', 'light'))

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Register blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(sertifikasi_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)
