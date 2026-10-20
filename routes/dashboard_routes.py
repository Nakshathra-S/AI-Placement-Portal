from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from routes.auth_routes import login_required
from database import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return redirect(url_for('auth.login_page'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_page():
    user = db.get_user_by_id(session['user_id'])
    stats = db.get_dashboard_stats(session['user_id'])
    return render_template('dashboard.html', user=user, stats=stats)

@dashboard_bp.route('/dashboard/stats')
@login_required
def dashboard_stats_api():
    stats = db.get_dashboard_stats(session['user_id'])
    return jsonify(stats)
