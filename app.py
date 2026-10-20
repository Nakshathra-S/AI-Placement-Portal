import os
import logging
from flask import Flask, render_template, jsonify
from config import Config
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('AIPlacementPortal')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Secret key for sessions
    app.secret_key = Config.SECRET_KEY

    # Initialize Database (MySQL or SQLite fallback)
    with app.app_context():
        try:
            db.init_db()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.technical_routes import technical_bp
    from routes.hr_routes import hr_bp
    from routes.gd_routes import gd_bp
    from routes.english_routes import english_bp
    from routes.history_routes import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(technical_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(gd_bp)
    app.register_blueprint(english_bp)
    app.register_blueprint(history_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="""
            <div class="portal-container" style="text-align: center; padding: 60px 20px;">
                <h1 style="font-size: 3rem; color: var(--primary);">404</h1>
                <h2>Page Not Found</h2>
                <p style="color: var(--text-muted); margin: 16px 0 24px;">The page you are looking for does not exist or has been moved.</p>
                <a href="/" class="btn btn-primary">Return to Portal</a>
            </div>
        """), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error occurred.'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = Config.PORT
    logger.info(f"Starting AI Placement Portal on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=(Config.FLASK_ENV == 'development'))
