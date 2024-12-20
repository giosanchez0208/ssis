import psycopg2
import os
import pymysql
from urllib.parse import urlparse
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, current_app

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

college_bp = Blueprint('college', __name__, url_prefix='/colleges')

@college_bp.route('/', methods=['GET'])
def list_colleges():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    sql_colleges = "SELECT * FROM colleges"
    sql_programs = "SELECT * FROM programs"
    
    cursor.execute(sql_colleges)
    colleges = cursor.fetchall()
    
    cursor.execute(sql_programs)
    programs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('colleges.html', colleges=colleges, programs=programs)

@college_bp.route('/create', methods=['POST'])
def create_college():
    data = request.get_json()
    college_code = data.get('college_code')
    college_name = data.get('college_name')

    if not college_name:
        return jsonify({'error': 'College name cannot be empty.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = "INSERT INTO colleges (college_code, college_name) VALUES (%s, %s)"
        cursor.execute(sql, (college_code, college_name))
        conn.commit()
        return jsonify({'success': 'College created successfully.'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'College code already exists.'}), 400
    finally:
        cursor.close()
        conn.close()

@college_bp.route('/update', methods=['POST'])
def update_college():
    data = request.get_json()
    original_code = data['original_code']
    college_code = data['college_code']
    college_name = data['college_name']

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        check_sql = "SELECT * FROM colleges WHERE college_code = %s AND college_code != %s"
        cursor.execute(check_sql, (college_code, original_code))
        if cursor.fetchone():
            return jsonify({'message': 'College code already exists'}), 400

        update_sql = "UPDATE colleges SET college_code = %s, college_name = %s WHERE college_code = %s"
        cursor.execute(update_sql, (college_code, college_name, original_code))
        conn.commit()
        
        return jsonify({'message': 'College updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Update failed: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@college_bp.route('/delete', methods=['DELETE'])
def delete_college():
    college_code = request.json['college_code']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        delete_sql = "DELETE FROM colleges WHERE college_code = %s"
        cursor.execute(delete_sql, (college_code,))
        conn.commit()
        return jsonify({'message': 'College deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Delete failed: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@college_bp.route('/check_code', methods=['POST'])
def check_duplicate_college_code():
    college_code = request.json['college_code']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = "SELECT EXISTS(SELECT 1 FROM colleges WHERE college_code = %s)"
        cursor.execute(sql, (college_code,))
        exists = cursor.fetchone()[0]
        return jsonify({'exists': exists})
    finally:
        cursor.close()
        conn.close()