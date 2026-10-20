from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from services import evaluation_service
from database import db

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/hr', methods=['GET'])
@login_required
def hr_page():
    return render_template('hr.html')

@hr_bp.route('/hr/questions', methods=['GET'])
@login_required
def get_questions():
    questions = evaluation_service.get_hr_questions()
    return jsonify({
        'success': True,
        'questions': questions
    })

@hr_bp.route('/hr/evaluate', methods=['POST'])
@login_required
def evaluate_hr():
    data = request.get_json() or {}
    question_text = (data.get('question_text') or '').strip()
    submitted_answer = (data.get('submitted_answer') or '').strip()

    if not question_text:
        return jsonify({'success': False, 'message': 'Question text is required.'}), 400

    if not submitted_answer:
        return jsonify({'success': False, 'message': 'Please provide an answer to evaluate.'}), 400

    evaluation = evaluation_service.evaluate_hr_answer(question_text, submitted_answer)

    # Save to database
    attempt_id = db.insert_hr_attempt(
        user_id=session['user_id'],
        question_text=question_text,
        submitted_answer=submitted_answer,
        score=evaluation['score'],
        score_breakdown=evaluation.get('score_breakdown'),
        feedback=evaluation.get('feedback'),
        strengths=evaluation.get('strengths'),
        weaknesses=evaluation.get('weaknesses'),
        model_answer=evaluation.get('model_answer'),
        suggestions=evaluation.get('suggestions')
    )

    evaluation['attempt_id'] = attempt_id
    evaluation['success'] = True
    return jsonify(evaluation)

@hr_bp.route('/hr/history', methods=['GET'])
@login_required
def hr_history():
    history = db.get_user_history(session['user_id'])
    hr_history = [h for h in history if h['module_type'] == 'hr']
    return jsonify({'success': True, 'attempts': hr_history})
