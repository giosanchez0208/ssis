import os
from datetime import timedelta
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

class Config:

    BASE_DIR = Path(__file__).resolve().parent

    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }

    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

class DevelopmentConfig(Config):
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    SESSION_COOKIE_SECURE = False  # allow "http"

def create_app(config_class=DevelopmentConfig):

    app = Flask(__name__,
                template_folder=config_class.TEMPLATE_FOLDER,
                static_folder=config_class.STATIC_FOLDER)
    
    app.config.from_object(config_class)

    from routes.student_routes import student_bp
    from routes.program_routes import program_bp
    from routes.college_routes import college_bp
    from routes.cloudinary_routes import cloudinary_bp 
    
    app.register_blueprint(student_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(cloudinary_bp)
    
    @app.route('/')
    def home():
        from flask import redirect, url_for
        return redirect(url_for('student.list_students'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()