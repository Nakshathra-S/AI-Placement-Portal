import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-placement-portal-secret-key-default-2026')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    PORT = int(os.getenv('PORT', 5000))
    
    # MySQL Database Config
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'ai_placement_portal')
    
    # Google Gemini API Config
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
