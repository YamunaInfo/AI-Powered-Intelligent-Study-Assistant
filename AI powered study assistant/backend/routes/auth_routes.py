from flask import Blueprint, request, jsonify
import mysql.connector
import hashlib

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Admin@123',
    'database': 'study_assistant'
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    db     = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute(
        'SELECT id, name, email FROM users WHERE email = %s AND password = %s',
        (email, hash_password(password))
    )
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'name':    user[1],
            'email':   user[2]
        })
    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data     = request.json
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    db     = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()

    try:
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
            (name, email, hash_password(password))
        )
        db.commit()
        user_id = cursor.lastrowid
    except mysql.connector.IntegrityError:
        db.close()
        return jsonify({'message': 'Email already exists'}), 400

    db.close()
    # ✅ JS checks for 'Signup successful' — keep this consistent
    return jsonify({'message': 'Signup successful', 'user_id': user_id})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})
