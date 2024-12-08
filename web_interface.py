from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from config import *
from logger import access_logger, api_logger, log_access, log_api_call
from functools import wraps
import os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, 
    resources={
        r"/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True,
            "max_age": 3600
        }
    }
)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def log_request_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log la requête
        log_access(request, 200)  # Code initial avant de connaître le vrai code
        
        # Exécute la vue
        response = f(*args, **kwargs)
        
        # Si c'est une route API, log plus de détails
        if request.path.startswith('/api/'):
            log_api_call(request, response)
        
        return response
    return decorated_function

@app.before_request
def log_request_info():
    access_logger.info(
        f"Request: {request.method} {request.url} - "
        f"IP: {request.remote_addr} - "
        f"User-Agent: {request.headers.get('User-Agent')} - "
        f"Authenticated: {current_user.is_authenticated}"
    )

@app.after_request
def log_response_info(response):
    access_logger.info(
        f"Response: {response.status} - "
        f"Size: {response.content_length} bytes"
    )
    return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def get_attacks(limit=100):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, ip_address, attack_type, username, password, payload, headers, additional_info 
        FROM attacks 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    attacks = c.fetchall()
    conn.close()
    return attacks

def get_attack_stats():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Statistiques par type d'attaque
    c.execute("""
        SELECT attack_type, COUNT(*) as count 
        FROM attacks 
        GROUP BY attack_type
    """)
    attack_types = dict(c.fetchall())
    
    # Top 5 des IP malveillantes
    c.execute("""
        SELECT ip_address, COUNT(*) as count 
        FROM attacks 
        GROUP BY ip_address 
        ORDER BY count DESC 
        LIMIT 5
    """)
    top_ips = dict(c.fetchall())
    
    conn.close()
    return {
        'attack_types': attack_types,
        'top_ips': top_ips
    }

@app.route('/')
@login_required
@log_request_response
def dashboard():
    attacks = get_attacks()
    stats = get_attack_stats()
    return render_template('dashboard.html', attacks=attacks, stats=stats)

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Add your authentication logic here
        if username == "admin" and password == "admin":  # Replace with your actual authentication
            user = User(username)
            login_user(user)
            response = make_response(jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {"username": username}
            }))
            return response
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

@app.route('/error')
def error_page():
    return "An error occurred while trying to load the external page. Please try again later."

@app.route('/logout')
@login_required
@log_request_response
def logout():
    access_logger.info(f"User logged out: {current_user.id}")
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/attacks')
@login_required
@log_request_response
def get_attacks_api():
    attacks = get_attacks()
    return jsonify([{
        'timestamp': attack[0],
        'ip_address': attack[1],
        'attack_type': attack[2],
        'username': attack[3],
        'password': attack[4],
        'payload': attack[5],
        'headers': attack[6],
        'additional_info': attack[7]
    } for attack in attacks])

@app.route('/api/stats')
@login_required
@log_request_response
def get_stats_api():
    return jsonify(get_attack_stats())

@app.route('/logs')
@login_required
@log_request_response
def view_logs():
    log_type = request.args.get('type', 'all')
    
    def get_log_content(file_name):
        try:
            with open(os.path.join('logs', file_name), 'r') as f:
                return f.read().split('\n')[-100:]  # Dernières 100 lignes
        except FileNotFoundError:
            return []
    
    logs = {
        'system': get_log_content(LOG_FILE),
        'access': get_log_content(ACCESS_LOG_FILE),
        'api': get_log_content(API_LOG_FILE),
        'attacks': get_log_content(ATTACK_LOG_FILE)
    }
    
    return render_template('logs.html', logs=logs, current_type=log_type)

if __name__ == '__main__':
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=6000)
