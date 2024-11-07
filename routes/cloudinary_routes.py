import os
from flask import Blueprint, request, jsonify, current_app
from models import db, StudentModel
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import logging

cloudinary_bp = Blueprint('cloudinary', __name__, url_prefix='/cloudinary')

@cloudinary_bp.route('/test_config', methods=['GET'])
def test_config():
    """Test route to verify Cloudinary configuration"""
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
    """Upload a new image to Cloudinary"""
    print("Upload route hit")  # Debug print
    
    if 'image' not in request.files:
        print("No image file in request")  # Debug print
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
        print("Attempting Cloudinary upload")  # Debug print
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )
        print(f"Upload successful: {upload_result}")  # Debug print
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
    except Exception as e:
        print(f"Upload failed with error: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cloudinary_bp.route('/update', methods=['POST'])
def update_image():
    """Update an existing image"""
    print("Update route hit")  # Debug print
    
    if 'image' not in request.files or 'student_id' not in request.form:
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
        
    file = request.files['image']
    student_id = request.form['student_id']
    
    try:
        # Get the student
        student = StudentModel.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
            
        # If there's an existing image, delete it
        if student.profile_picture_id:
            try:
                cloudinary.uploader.destroy(student.profile_picture_id)
            except Exception as e:
                print(f"Error deleting old image: {str(e)}")  # Debug print
                
        # Upload new image
        print("Attempting Cloudinary upload for update")  # Debug print
        upload_result = cloudinary.uploader.upload(
            file,
            folder='student_profiles',
            allowed_formats=['jpg', 'png', 'jpeg'],
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        )
        print(f"Update upload successful: {upload_result}")  # Debug print
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
    except Exception as e:
        print(f"Update failed with error: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500