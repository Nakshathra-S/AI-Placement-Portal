from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import db

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith(('/technical/', '/hr/', '/gd/', '/english/', '/history', '/dashboard/stats')):
                return jsonify({'error': 'Unauthorized. Please sign in.'}), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json() if request.is_json else request.form
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    if not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    # Login successful
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'redirect': url_for('dashboard.dashboard_page')
    })

@auth_bp.route('/register', methods=['POST'])
def register_api():
    data = request.get_json() if request.is_json else request.form
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long.'}), 400

    # Check if user already exists
    existing = db.get_user_by_email(email)
    if existing:
        return jsonify({'success': False, 'message': 'An account with this email already exists.'}), 409

    hashed_pw = generate_password_hash(password)
    user_id = db.create_user(name, email, hashed_pw)

    # Automatically sign in new user
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Account created successfully.',
        'redirect': url_for('dashboard.dashboard_page')
    }), 201

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email']
    })
