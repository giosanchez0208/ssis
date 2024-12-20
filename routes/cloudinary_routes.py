from flask import Blueprint, request, jsonify
import cloudinary.uploader
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

cloudinary_bp = Blueprint('cloudinary', __name__, url_prefix='/cloudinary')

# Database connection setup
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@cloudinary_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        upload_result = cloudinary.uploader.upload(file)
        url = upload_result.get('url')
        public_id = upload_result.get('public_id')

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO images (url, public_id) VALUES (%s, %s)"
                cursor.execute(sql, (url, public_id))
            connection.commit()
            return jsonify({'url': url, 'public_id': public_id}), 201
        except pymysql.MySQLError as e:
            connection.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cloudinary_bp.route('/delete', methods=['POST'])
def delete_image():
    data = request.get_json()
    public_id = data.get('public_id')

    if not public_id:
        return jsonify({'error': 'No public_id provided'}), 400

    try:
        cloudinary.uploader.destroy(public_id)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM images WHERE public_id = %s"
                cursor.execute(sql, (public_id,))
            connection.commit()
            return jsonify({'success': True}), 200
        except pymysql.MySQLError as e:
            connection.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500