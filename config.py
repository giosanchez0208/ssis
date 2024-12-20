import os
from datetime import timedelta
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent

    SECRET_KEY = os.getenv('SECRET_KEY')
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

def create_app():
    from flask import Flask
    
    app = Flask(__name__,
                template_folder=Config.TEMPLATE_FOLDER,
                static_folder=Config.STATIC_FOLDER)
    
    app.config.from_object(Config)
    
    from routes.student_routes import student_bp
    from routes.program_routes import program_bp
    from routes.college_routes import college_bp
    from routes.cloudinary_routes import cloudinary_bp 
    from routes.home import home_bp
    
    app.register_blueprint(home_bp)
    
    app.register_blueprint(student_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(cloudinary_bp)
    
    return app