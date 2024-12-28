import os
from flask import Blueprint, request, jsonify, current_app
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from controllers.db_controller import (
    get_student_profile_picture_id,
    update_profile_picture_id,
    remove_profile_picture,
    fetch_single_student
)

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
        student = fetch_single_student(student_id)
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404

        old_picture_id = get_student_profile_picture_id(student_id)
        if old_picture_id:
            try:
                cloudinary.uploader.destroy(old_picture_id)
            except Exception as e:
                current_app.logger.error(f"Error deleting old image: {str(e)}")
                
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )

        update_profile_picture_id(student_id, upload_result['public_id'])
        
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

@cloudinary_bp.route('/delete/<student_id>', methods=['POST'])
def delete_image(student_id):
    try:
        
        picture_id = get_student_profile_picture_id(student_id)
        if not picture_id:
            return jsonify({
                'success': False,
                'error': 'No profile picture found'
            }), 404
        try:
            cloudinary.uploader.destroy(picture_id)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f"Error deleting image: {str(e)}"
            }), 500

        remove_profile_picture(student_id)
        
        return jsonify({
            'success': True,
            'message': 'Profile picture deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500