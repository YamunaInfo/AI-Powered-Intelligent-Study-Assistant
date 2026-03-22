from flask import Blueprint, request, jsonify
import mysql.connector
from ai_engine import (
    generate_summary,
    extract_keywords,
    generate_questions,
    detect_concept_gap,
    generate_voice_explanation
)

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Admin@123',
    'database': 'study_assistant'
}


@ai_bp.route('/generate-summary', methods=['POST'])
def api_generate_summary():
    data = request.json
    note_id = data.get('note_id')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute('SELECT note_text FROM notes WHERE id = %s', (note_id,))
    note = cursor.fetchone()
    db.close()

    if note:
        summary = generate_summary(note[0])
        return jsonify({'summary': summary})

    return jsonify({'message': 'Note not found'}), 404


@ai_bp.route('/extract-keywords', methods=['POST'])
def api_extract_keywords():
    data = request.json
    note_id = data.get('note_id')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute('SELECT note_text FROM notes WHERE id = %s', (note_id,))
    note = cursor.fetchone()
    db.close()

    if note:
        keywords = extract_keywords(note[0])
        return jsonify({'keywords': keywords})

    return jsonify({'message': 'Note not found'}), 404


@ai_bp.route('/generate-questions', methods=['POST'])
def api_generate_questions():
    data = request.json
    note_id = data.get('note_id')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute('SELECT note_text FROM notes WHERE id = %s', (note_id,))
    note = cursor.fetchone()

    if note:
        questions = generate_questions(note[0])

        for q in questions:
            cursor.execute(
                'INSERT INTO questions (note_id, question) VALUES (%s, %s)',
                (note_id, q)
            )

        db.commit()
        db.close()

        return jsonify({'questions': questions})

    db.close()
    return jsonify({'message': 'Note not found'}), 404


@ai_bp.route('/submit-answer', methods=['POST'])
def api_submit_answer():
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')

    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()
    cursor.execute('SELECT question FROM questions WHERE id = %s', (question_id,))
    q = cursor.fetchone()

    if q:
        expected = q[0]
        gap = detect_concept_gap(user_answer, expected)
        score = gap['score']

        cursor.execute(
            'INSERT INTO answers (question_id, user_answer, score) VALUES (%s, %s, %s)',
            (question_id, user_answer, score)
        )

        db.commit()
        db.close()

        return jsonify({'score': score, 'gap': gap})

    db.close()
    return jsonify({'message': 'Question not found'}), 404


@ai_bp.route('/detect-concept-gap', methods=['POST'])
def api_detect_concept_gap():
    data = request.json
    gap = detect_concept_gap(
        data.get('student_answer'),
        data.get('expected_answer')
    )
    return jsonify(gap)


@ai_bp.route('/voice-explanation', methods=['POST'])
def api_voice_explanation():
    data = request.json
    explanation = generate_voice_explanation(data.get('concept'))
    return jsonify({'explanation': explanation})
