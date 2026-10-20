from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from services import evaluation_service
from database import db

gd_bp = Blueprint('gd', __name__)

@gd_bp.route('/gd', methods=['GET'])
@login_required
def gd_page():
    return render_template('gd.html')

@gd_bp.route('/gd/generate-topic', methods=['POST'])
@login_required
def generate_topic():
    topic_data = evaluation_service.get_gd_topic()
    return jsonify({
        'success': True,
        'data': topic_data
    })

@gd_bp.route('/gd/evaluate', methods=['POST'])
@login_required
def evaluate_gd():
    data = request.get_json() or {}
    topic = (data.get('topic') or '').strip()
    submitted_opinion = (data.get('submitted_opinion') or '').strip()

    if not topic:
        return jsonify({'success': False, 'message': 'Discussion topic is required.'}), 400

    if not submitted_opinion:
        return jsonify({'success': False, 'message': 'Please provide your discussion contribution.'}), 400

    evaluation = evaluation_service.evaluate_gd_opinion(topic, submitted_opinion)

    # Save to database
    attempt_id = db.insert_gd_attempt(
        user_id=session['user_id'],
        topic=topic,
        submitted_opinion=submitted_opinion,
        score=evaluation['score'],
        score_breakdown=evaluation.get('score_breakdown'),
        feedback=evaluation.get('feedback'),
        strengths=evaluation.get('strengths'),
        weaknesses=evaluation.get('weaknesses'),
        counterarguments=evaluation.get('counterarguments'),
        model_discussion=evaluation.get('model_discussion')
    )

    evaluation['attempt_id'] = attempt_id
    evaluation['success'] = True
    return jsonify(evaluation)

@gd_bp.route('/gd/history', methods=['GET'])
@login_required
def gd_history():
    history = db.get_user_history(session['user_id'])
    gd_history = [h for h in history if h['module_type'] == 'gd']
    return jsonify({'success': True, 'attempts': gd_history})
