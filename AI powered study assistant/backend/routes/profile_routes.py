from flask import Blueprint, request, jsonify
import mysql.connector

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Admin@123',
    'database': 'study_assistant'
}

@profile_bp.route('/', methods=['GET'])
def get_profile():
    user_id = request.args.get('user_id')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute(
        'SELECT name, email, created_at FROM users WHERE id = %s',
        (user_id,)
    )
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            'name': user[0],
            'email': user[1],
            'created_at': str(user[2])
        })

    return jsonify({'message': 'User not found'}), 404


@profile_bp.route('/progress', methods=['GET'])
def get_progress():
    user_id = request.args.get('user_id')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()

    cursor.execute(
        'SELECT questions_attempted, concept_gaps_detected FROM progress WHERE user_id = %s',
        (user_id,)
    )
    progress = cursor.fetchone()

    if not progress:
        cursor.execute(
            'INSERT INTO progress (user_id) VALUES (%s)',
            (user_id,)
        )
        db.commit()
        progress = (0, 0)

    db.close()

    return jsonify({
        'questions_attempted': progress[0],
        'concept_gaps_detected': progress[1]
    })
