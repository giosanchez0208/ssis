import os
from datetime import timedelta
from pathlib import Path

class Config:
    """Base configuration class."""
    
    # Base directory of the project
    BASE_DIR = Path(__file__).resolve().parent

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }

    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:guerrillaRdio@localhost/ssis_db'
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = False
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/ssis_test_db'
    WTF_CSRF_ENABLED = False  # Disable CSRF tokens in tests

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost/ssis_db')
    
    # Additional security settings for production
    SESSION_COOKIE_SECURE = True
    SECURITY_HEADERS = {
        **Config.SECURITY_HEADERS,
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }

def create_app(config_class=DevelopmentConfig):
    """Application factory function."""
    from flask import Flask
    from models import db
    
    app = Flask(__name__,
                template_folder=config_class.TEMPLATE_FOLDER,
                static_folder=config_class.STATIC_FOLDER)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.student_routes import student_bp
    from routes.program_routes import program_bp
    from routes.college_routes import college_bp
    from routes.cloudinary_routes import cloudinary_bp 
    
    app.register_blueprint(student_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(cloudinary_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to response."""
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        return response
    
    @app.route('/')
    def home():
        from flask import redirect, url_for
        return redirect(url_for('student.list_students'))
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        from flask import render_template
        db.session.rollback()  # Roll back session in case of database error
        return render_template('errors/500.html'), 500
    
    return app

# Configuration dictionary for easy access to different configs
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

if __name__ == '__main__':
    app = create_app()
    app.run()