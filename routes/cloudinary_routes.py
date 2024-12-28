import os
from flask import Blueprint, request, jsonify, current_app
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import logging
from controllers.db_controller import get_db_connection

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
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
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
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT profile_picture_id FROM students WHERE id_num = %s', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
            
        if student['profile_picture_id']:
            try:
                cloudinary.uploader.destroy(student['profile_picture_id'])
            except Exception as e:
                print(f"Error deleting old image: {str(e)}")
                
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )
        
        cursor.execute('UPDATE students SET profile_picture_id = %s WHERE id_num = %s', 
                      (upload_result['public_id'], student_id))
        conn.commit()
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@cloudinary_bp.route('/delete/<student_id>', methods=['POST'])
def delete_image(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT profile_picture_id FROM students WHERE id_num = %s', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
            
        if student['profile_picture_id']:
            try:
                cloudinary.uploader.destroy(student['profile_picture_id'])
                cursor.execute('UPDATE students SET profile_picture_id = NULL WHERE id_num = %s', (student_id,))
                conn.commit()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f"Error deleting image: {str(e)}"
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Profile picture deleted successfully'
        })
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()