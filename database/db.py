import os
import sqlite3
import json
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

# Database mode: 'mysql' or 'sqlite' (fallback)
DB_MODE = 'mysql'

def get_mysql_connection(database=None):
    import mysql.connector
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=database or Config.DB_NAME,
        charset='utf8mb4'
    )

def get_sqlite_path():
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'instance')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'ai_placement_portal.db')

def get_connection():
    global DB_MODE
    if DB_MODE == 'mysql':
        try:
            return get_mysql_connection(Config.DB_NAME)
        except Exception as e:
            logger.warning(f"MySQL connection failed ({e}). Switching to SQLite fallback engine.")
            DB_MODE = 'sqlite'
    
    # SQLite connection
    conn = sqlite3.connect(get_sqlite_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global DB_MODE
    logger.info("Initializing database...")
    
    # Try initializing MySQL first
    try:
        import mysql.connector
        # Connect to MySQL server without selecting database
        root_conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = root_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        root_conn.close()

        # Connect to newly created/verified database
        conn = get_mysql_connection(Config.DB_NAME)
        cursor = conn.cursor()
        
        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            for stmt in statements:
                # Skip USE and CREATE DATABASE here as already handled
                if stmt.upper().startswith('USE ') or stmt.upper().startswith('CREATE DATABASE'):
                    continue
                cursor.execute(stmt)
            conn.commit()
        cursor.close()
        conn.close()
        DB_MODE = 'mysql'
        logger.info("MySQL database initialized successfully.")
        return
    except Exception as e:
        logger.warning(f"Could not initialize MySQL ({e}). Initializing local SQLite fallback...")
        DB_MODE = 'sqlite'

    # Initialize SQLite database
    conn = sqlite3.connect(get_sqlite_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technical_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_role TEXT NOT NULL,
            question_number INTEGER DEFAULT 1,
            question_text TEXT NOT NULL,
            submitted_answer TEXT NOT NULL,
            score REAL NOT NULL,
            score_breakdown TEXT,
            feedback TEXT,
            strengths TEXT,
            missing_concepts TEXT,
            model_answer TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hr_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            submitted_answer TEXT NOT NULL,
            score REAL NOT NULL,
            score_breakdown TEXT,
            feedback TEXT,
            strengths TEXT,
            weaknesses TEXT,
            model_answer TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gd_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            submitted_opinion TEXT NOT NULL,
            score REAL NOT NULL,
            score_breakdown TEXT,
            feedback TEXT,
            strengths TEXT,
            weaknesses TEXT,
            counterarguments TEXT,
            model_discussion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS english_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            input_text TEXT NOT NULL,
            score REAL NOT NULL,
            status_badge TEXT NOT NULL,
            readiness_percentage INTEGER NOT NULL,
            clarity_score REAL,
            grammar_score REAL,
            structure_score REAL,
            tone_score REAL,
            vocabulary_score REAL,
            corrections TEXT,
            corrected_text TEXT,
            feedback TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("SQLite database fallback initialized successfully.")

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    global DB_MODE
    conn = get_connection()
    try:
        # SQLite uses ? while MySQL uses %s
        if DB_MODE == 'sqlite':
            # Replace %s with ? safely
            adapted_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(adapted_query, params)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                return last_id
            if fetchone:
                row = cursor.fetchone()
                return dict(row) if row else None
            if fetchall:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            return None
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
            if fetchone:
                row = cursor.fetchone()
                cursor.close()
                return row
            if fetchall:
                rows = cursor.fetchall()
                cursor.close()
                return rows
            cursor.close()
            return None
    finally:
        conn.close()

# ---------------- USER REPOSITORY ----------------

def get_user_by_email(email):
    query = "SELECT user_id, name, email, password_hash, created_at FROM users WHERE email = %s"
    return execute_query(query, (email.strip().lower(),), fetchone=True)

def get_user_by_id(user_id):
    query = "SELECT user_id, name, email, created_at FROM users WHERE user_id = %s"
    return execute_query(query, (user_id,), fetchone=True)

def create_user(name, email, password_hash):
    query = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
    return execute_query(query, (name.strip(), email.strip().lower(), password_hash), commit=True)

# ---------------- ATTEMPT INSERTIONS ----------------

def insert_technical_attempt(user_id, job_role, question_number, question_text, submitted_answer, score, score_breakdown, feedback, strengths, missing_concepts, model_answer, suggestions):
    query = """
        INSERT INTO technical_attempts 
        (user_id, job_role, question_number, question_text, submitted_answer, score, score_breakdown, feedback, strengths, missing_concepts, model_answer, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if isinstance(score_breakdown, (dict, list)):
        score_breakdown = json.dumps(score_breakdown)
    if isinstance(missing_concepts, (dict, list)):
        missing_concepts = json.dumps(missing_concepts)
    if isinstance(suggestions, (dict, list)):
        suggestions = json.dumps(suggestions)
        
    return execute_query(query, (
        user_id, job_role, question_number, question_text, submitted_answer,
        score, score_breakdown, feedback, strengths, missing_concepts, model_answer, suggestions
    ), commit=True)

def insert_hr_attempt(user_id, question_text, submitted_answer, score, score_breakdown, feedback, strengths, weaknesses, model_answer, suggestions):
    query = """
        INSERT INTO hr_attempts
        (user_id, question_text, submitted_answer, score, score_breakdown, feedback, strengths, weaknesses, model_answer, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if isinstance(score_breakdown, (dict, list)):
        score_breakdown = json.dumps(score_breakdown)
    if isinstance(suggestions, (dict, list)):
        suggestions = json.dumps(suggestions)
        
    return execute_query(query, (
        user_id, question_text, submitted_answer, score, score_breakdown,
        feedback, strengths, weaknesses, model_answer, suggestions
    ), commit=True)

def insert_gd_attempt(user_id, topic, submitted_opinion, score, score_breakdown, feedback, strengths, weaknesses, counterarguments, model_discussion):
    query = """
        INSERT INTO gd_attempts
        (user_id, topic, submitted_opinion, score, score_breakdown, feedback, strengths, weaknesses, counterarguments, model_discussion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if isinstance(score_breakdown, (dict, list)):
        score_breakdown = json.dumps(score_breakdown)
    if isinstance(counterarguments, (dict, list)):
        counterarguments = json.dumps(counterarguments)
        
    return execute_query(query, (
        user_id, topic, submitted_opinion, score, score_breakdown,
        feedback, strengths, weaknesses, counterarguments, model_discussion
    ), commit=True)

def insert_english_attempt(user_id, input_text, score, status_badge, readiness_percentage, clarity_score, grammar_score, structure_score, tone_score, vocabulary_score, corrections, corrected_text, feedback, suggestions):
    query = """
        INSERT INTO english_attempts
        (user_id, input_text, score, status_badge, readiness_percentage, clarity_score, grammar_score, structure_score, tone_score, vocabulary_score, corrections, corrected_text, feedback, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if isinstance(corrections, (dict, list)):
        corrections = json.dumps(corrections)
    if isinstance(suggestions, (dict, list)):
        suggestions = json.dumps(suggestions)

    return execute_query(query, (
        user_id, input_text, score, status_badge, readiness_percentage,
        clarity_score, grammar_score, structure_score, tone_score, vocabulary_score,
        corrections, corrected_text, feedback, suggestions
    ), commit=True)

# ---------------- UNIFIED HISTORY & STATS ----------------

def format_timestamp(ts):
    if not ts:
        return ""
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace('Z', ''))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return ts
    if hasattr(ts, 'strftime'):
        return ts.strftime('%Y-%m-%d %H:%M:%S')
    return str(ts)

def get_user_history(user_id, limit=100):
    """
    Returns unified chronological history matching Screenshot 5:
    Badge: e.g. ENGLISH CHECKER, WORK FROM HOME, FULL STACK DEVELOPER, HR INTERVIEW
    Title: Attempt Record #<id>
    Score: X/10 with status color
    Date/time string
    Full diagnostic report payload for accordion expansion
    """
    # 1. Technical attempts
    tech_sql = """
        SELECT attempt_id, user_id, job_role, question_text, submitted_answer, score,
               score_breakdown, feedback, strengths, missing_concepts, model_answer, suggestions, created_at
        FROM technical_attempts WHERE user_id = %s
    """
    tech_rows = execute_query(tech_sql, (user_id,), fetchall=True) or []
    
    # 2. HR attempts
    hr_sql = """
        SELECT attempt_id, user_id, question_text, submitted_answer, score,
               score_breakdown, feedback, strengths, weaknesses, model_answer, suggestions, created_at
        FROM hr_attempts WHERE user_id = %s
    """
    hr_rows = execute_query(hr_sql, (user_id,), fetchall=True) or []
    
    # 3. GD attempts
    gd_sql = """
        SELECT attempt_id, user_id, topic, submitted_opinion, score,
               score_breakdown, feedback, strengths, weaknesses, counterarguments, model_discussion, created_at
        FROM gd_attempts WHERE user_id = %s
    """
    gd_rows = execute_query(gd_sql, (user_id,), fetchall=True) or []
    
    # 4. English attempts
    eng_sql = """
        SELECT attempt_id, user_id, input_text, score, status_badge, readiness_percentage,
               clarity_score, grammar_score, structure_score, tone_score, vocabulary_score,
               corrections, corrected_text, feedback, suggestions, created_at
        FROM english_attempts WHERE user_id = %s
    """
    eng_rows = execute_query(eng_sql, (user_id,), fetchall=True) or []

    history = []

    # Map Technical
    for r in tech_rows:
        badge = r['job_role'].upper() if r.get('job_role') else "TECHNICAL"
        history.append({
            'attempt_id': r['attempt_id'],
            'module_type': 'technical',
            'badge_label': badge,
            'title': f"Attempt Record #{r['attempt_id']}",
            'score': float(r['score']),
            'created_at': format_timestamp(r['created_at']),
            'raw_date': str(r['created_at']),
            'details': {
                'job_role': r.get('job_role'),
                'question': r.get('question_text'),
                'answer': r.get('submitted_answer'),
                'score_breakdown': r.get('score_breakdown'),
                'feedback': r.get('feedback'),
                'strengths': r.get('strengths'),
                'missing_concepts': r.get('missing_concepts'),
                'model_answer': r.get('model_answer'),
                'suggestions': r.get('suggestions')
            }
        })

    # Map HR
    for r in hr_rows:
        history.append({
            'attempt_id': r['attempt_id'],
            'module_type': 'hr',
            'badge_label': "HR INTERVIEW",
            'title': f"Attempt Record #{r['attempt_id']}",
            'score': float(r['score']),
            'created_at': format_timestamp(r['created_at']),
            'raw_date': str(r['created_at']),
            'details': {
                'question': r.get('question_text'),
                'answer': r.get('submitted_answer'),
                'score_breakdown': r.get('score_breakdown'),
                'feedback': r.get('feedback'),
                'strengths': r.get('strengths'),
                'weaknesses': r.get('weaknesses'),
                'model_answer': r.get('model_answer'),
                'suggestions': r.get('suggestions')
            }
        })

    # Map GD
    for r in gd_rows:
        topic_title = r.get('topic', 'GROUP DISCUSSION').upper()
        # Clean topic title for badge if long
        badge = topic_title if len(topic_title) <= 25 else "GROUP DISCUSSION"
        history.append({
            'attempt_id': r['attempt_id'],
            'module_type': 'gd',
            'badge_label': badge,
            'title': f"Attempt Record #{r['attempt_id']}",
            'score': float(r['score']),
            'created_at': format_timestamp(r['created_at']),
            'raw_date': str(r['created_at']),
            'details': {
                'topic': r.get('topic'),
                'opinion': r.get('submitted_opinion'),
                'score_breakdown': r.get('score_breakdown'),
                'feedback': r.get('feedback'),
                'strengths': r.get('strengths'),
                'weaknesses': r.get('weaknesses'),
                'counterarguments': r.get('counterarguments'),
                'model_discussion': r.get('model_discussion')
            }
        })

    # Map English
    for r in eng_rows:
        history.append({
            'attempt_id': r['attempt_id'],
            'module_type': 'english',
            'badge_label': "ENGLISH CHECKER",
            'title': f"Attempt Record #{r['attempt_id']}",
            'score': float(r['score']),
            'created_at': format_timestamp(r['created_at']),
            'raw_date': str(r['created_at']),
            'details': {
                'input_text': r.get('input_text'),
                'status_badge': r.get('status_badge'),
                'readiness_percentage': r.get('readiness_percentage'),
                'clarity_score': float(r.get('clarity_score', 0) or 0),
                'grammar_score': float(r.get('grammar_score', 0) or 0),
                'structure_score': float(r.get('structure_score', 0) or 0),
                'tone_score': float(r.get('tone_score', 0) or 0),
                'vocabulary_score': float(r.get('vocabulary_score', 0) or 0),
                'corrections': r.get('corrections'),
                'corrected_text': r.get('corrected_text'),
                'feedback': r.get('feedback'),
                'suggestions': r.get('suggestions')
            }
        })

    # Sort descending by raw_date / timestamp
    history.sort(key=lambda x: x['raw_date'], reverse=True)
    return history[:limit]

def delete_attempt(user_id, module_type, attempt_id):
    tables = {
        'technical': 'technical_attempts',
        'hr': 'hr_attempts',
        'gd': 'gd_attempts',
        'english': 'english_attempts'
    }
    table_name = tables.get(module_type.lower())
    if not table_name:
        return False
    
    query = f"DELETE FROM {table_name} WHERE attempt_id = %s AND user_id = %s"
    execute_query(query, (attempt_id, user_id), commit=True)
    return True

def delete_attempt_any(user_id, attempt_id):
    """Fallback deletion if module_type is omitted"""
    deleted = False
    for t in ['technical_attempts', 'hr_attempts', 'gd_attempts', 'english_attempts']:
        q = f"DELETE FROM {t} WHERE attempt_id = %s AND user_id = %s"
        execute_query(q, (attempt_id, user_id), commit=True)
    return True

def get_dashboard_stats(user_id):
    history = get_user_history(user_id, limit=500)
    total_attempts = len(history)
    if total_attempts == 0:
        return {
            'total_attempts': 0,
            'average_score': 0.0,
            'best_score': 0.0,
            'technical_attempts': 0,
            'hr_attempts': 0,
            'gd_attempts': 0,
            'english_attempts': 0,
            'recent_attempts': []
        }
    
    scores = [h['score'] for h in history]
    avg_score = round(sum(scores) / len(scores), 1)
    best_score = max(scores)
    
    module_counts = {'technical': 0, 'hr': 0, 'gd': 0, 'english': 0}
    for h in history:
        m = h.get('module_type', '')
        if m in module_counts:
            module_counts[m] += 1

    return {
        'total_attempts': total_attempts,
        'average_score': avg_score,
        'best_score': best_score,
        'technical_attempts': module_counts['technical'],
        'hr_attempts': module_counts['hr'],
        'gd_attempts': module_counts['gd'],
        'english_attempts': module_counts['english'],
        'recent_attempts': history[:5]
    }
