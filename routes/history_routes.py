from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from database import db

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@login_required
def history_page():
    return render_template('history.html')

@history_bp.route('/history/data', methods=['GET'])
@login_required
def history_data():
    attempts = db.get_user_history(session['user_id'], limit=100)
    return jsonify({
        'success': True,
        'attempts': attempts
    })

@history_bp.route('/history/<int:attempt_id>', methods=['DELETE'])
@history_bp.route('/history/<module_type>/<int:attempt_id>', methods=['DELETE'])
@login_required
def delete_attempt_record(attempt_id, module_type=None):
    user_id = session['user_id']
    
    if module_type:
        success = db.delete_attempt(user_id, module_type, attempt_id)
    else:
        success = db.delete_attempt_any(user_id, attempt_id)

    if success:
        return jsonify({'success': True, 'message': f'Record #{attempt_id} deleted successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Record could not be deleted.'}), 400
