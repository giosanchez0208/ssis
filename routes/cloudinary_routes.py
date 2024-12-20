from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify, current_app, url_for
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import pymysql
import os
from urllib.parse import urlparse

def get_db_connection():
    try:
        url = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost/studentdb')
        parsed_url = urlparse(url)
        
        conn = pymysql.connect(
            host=parsed_url.hostname,
            database=parsed_url.path.strip('/'),
            user=parsed_url.username,
            password=parsed_url.password,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except (Exception, pymysql.err.Error) as error:
        current_app.logger.error(f"Database connection failed: {error}")


cloudinary_bp = Blueprint('cloudinary', __name__, url_prefix='/cloudinary')

@cloudinary_bp.route('/test_config', methods=['GET'])
def test_config():
    try:
        return jsonify({
            'cloud_name': current_app.config['CLOUDINARY_CLOUD_NAME'],
            'api_key': current_app.config['CLOUDINARY_API_KEY'],
            'api_secret': 'exists' if current_app.config['CLOUDINARY_API_SECRET'] else 'missing'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cloudinary_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No image file provided'
        }), 400
        
    file = request.files['image']
    if not file:
        return jsonify({
            'success': False,
            'error': 'Empty file'
        }), 400
    
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            insert_sql = "INSERT INTO image_uploads (public_id, secure_url) VALUES (%s, %s) RETURNING id"
            cursor.execute(insert_sql, (upload_result['public_id'], upload_result['secure_url']))
            image_id = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'image_id': image_id
            })
        except Exception as db_error:
            conn.rollback()
            return jsonify({
                'success': False,
                'error': str(db_error)
            }), 500
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cloudinary_bp.route('/update', methods=['POST'])
def update_image():
    if 'image' not in request.files or 'student_id' not in request.form:
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
        
    file = request.files['image']
    student_id = request.form['student_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT profile_picture_id FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        old_picture_id = student['profile_picture_id']
        
        if old_picture_id:
            try:
                cloudinary.uploader.destroy(old_picture_id)
            except Exception as cloudinary_error:
                print(f"Error deleting old image: {str(cloudinary_error)}")
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )
        
        update_sql = """
        UPDATE students 
        SET profile_picture_url = %s, profile_picture_id = %s 
        WHERE id = %s
        """
        cursor.execute(update_sql, (
            upload_result['secure_url'], 
            upload_result['public_id'], 
            student_id
        ))
        conn.commit()
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        cursor.close()
        conn.close()