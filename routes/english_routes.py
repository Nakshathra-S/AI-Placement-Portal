from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from services import evaluation_service
from database import db

english_bp = Blueprint('english', __name__)

@english_bp.route('/english', methods=['GET'])
@login_required
def english_page():
    return render_template('english.html')

@english_bp.route('/english/analyze', methods=['POST'])
@login_required
def analyze_english():
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()

    if not text:
        return jsonify({'success': False, 'message': 'Please provide text to analyze.'}), 400

    result = evaluation_service.analyze_english_text(text)
    breakdown = result.get('score_breakdown', {})

    # Save to database
    attempt_id = db.insert_english_attempt(
        user_id=session['user_id'],
        input_text=text,
        score=result['score'],
        status_badge=result.get('status_badge', 'GOOD'),
        readiness_percentage=result.get('readiness_percentage', int(result['score'] * 10)),
        clarity_score=breakdown.get('clarity'),
        grammar_score=breakdown.get('grammar'),
        structure_score=breakdown.get('sentence_structure'),
        tone_score=breakdown.get('tone'),
        vocabulary_score=breakdown.get('vocabulary'),
        corrections=result.get('corrections'),
        corrected_text=result.get('corrected_text'),
        feedback=result.get('feedback'),
        suggestions=result.get('suggestions')
    )

    result['attempt_id'] = attempt_id
    result['success'] = True
    return jsonify(result)

@english_bp.route('/english/history', methods=['GET'])
@login_required
def english_history():
    history = db.get_user_history(session['user_id'])
    eng_history = [h for h in history if h['module_type'] == 'english']
    return jsonify({'success': True, 'attempts': eng_history})
