from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from services import evaluation_service
from database import db

technical_bp = Blueprint('technical', __name__)

@technical_bp.route('/technical', methods=['GET'])
@login_required
def technical_page():
    return render_template('technical.html')

@technical_bp.route('/technical/generate', methods=['POST'])
@login_required
def generate_questions():
    data = request.get_json() or {}
    job_role = data.get('job_role', 'Full Stack Developer')
    
    questions = evaluation_service.get_technical_questions(job_role)
    return jsonify({
        'success': True,
        'job_role': job_role,
        'questions': questions
    })

@technical_bp.route('/technical/evaluate', methods=['POST'])
@login_required
def evaluate_answer():
    data = request.get_json() or {}
    job_role = data.get('job_role', 'Full Stack Developer')
    question_number = int(data.get('question_number', 1))
    question_text = (data.get('question_text') or '').strip()
    submitted_answer = (data.get('submitted_answer') or '').strip()

    if not question_text:
        return jsonify({'success': False, 'message': 'Question text is required.'}), 400

    if not submitted_answer:
        return jsonify({'success': False, 'message': 'Please provide an answer to evaluate.'}), 400

    evaluation = evaluation_service.evaluate_technical_answer(job_role, question_text, submitted_answer)

    # Save to database
    attempt_id = db.insert_technical_attempt(
        user_id=session['user_id'],
        job_role=job_role,
        question_number=question_number,
        question_text=question_text,
        submitted_answer=submitted_answer,
        score=evaluation['score'],
        score_breakdown=evaluation.get('score_breakdown'),
        feedback=evaluation.get('feedback'),
        strengths=evaluation.get('strengths'),
        missing_concepts=evaluation.get('missing_concepts'),
        model_answer=evaluation.get('model_answer'),
        suggestions=evaluation.get('suggestions')
    )

    evaluation['attempt_id'] = attempt_id
    evaluation['success'] = True
    return jsonify(evaluation)

@technical_bp.route('/technical/history', methods=['GET'])
@login_required
def technical_history():
    history = db.get_user_history(session['user_id'])
    tech_history = [h for h in history if h['module_type'] == 'technical']
    return jsonify({'success': True, 'attempts': tech_history})
