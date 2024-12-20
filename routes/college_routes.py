from flask import Blueprint, render_template, request, jsonify
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

college_bp = Blueprint('college', __name__, url_prefix='/colleges')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@college_bp.route('/', methods=['GET'])
def list_colleges():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM colleges")
            colleges = cursor.fetchall()
            cursor.execute("SELECT * FROM programs")
            programs = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('colleges.html', colleges=colleges, programs=programs)

@college_bp.route('/create', methods=['POST'])
def create_college():
    data = request.get_json()
    college_code = data.get('college_code')
    college_name = data.get('college_name')

    if not college_name:
        return jsonify({'error': 'College name cannot be empty.'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO colleges (college_code, college_name) VALUES (%s, %s)"
            cursor.execute(sql, (college_code, college_name))
        connection.commit()
        return jsonify({'success': 'College created successfully.'}), 201
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

@college_bp.route('/update', methods=['POST'])
def update_college():
    data = request.get_json()
    college_code = data.get('college_code')
    college_name = data.get('college_name')
    original_code = data.get('original_code')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE colleges
                SET college_code = %s, college_name = %s
                WHERE college_code = %s
            """
            cursor.execute(sql, (college_code, college_name, original_code))
        connection.commit()
        return jsonify({'success': 'College updated successfully.'}), 200
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

@college_bp.route('/delete', methods=['DELETE'])
def delete_college():
    data = request.get_json()
    college_code = data.get('college_code')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM colleges WHERE college_code = %s"
            cursor.execute(sql, (college_code,))
        connection.commit()
        return jsonify({'success': 'College deleted successfully.'}), 200
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

@college_bp.route('/<college_code>/info', methods=['GET'])
def get_college_info(college_code):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.course_code, p.course_name, COUNT(s.id_num) AS student_count
                FROM programs p
                LEFT JOIN students s ON p.course_code = s.course
                WHERE p.college = %s
                GROUP BY p.course_code, p.course_name
            """, (college_code,))
            courses = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(s.id_num) AS total_students
                FROM students s
                JOIN programs p ON s.course = p.course_code
                WHERE p.college = %s
            """, (college_code,))
            total_students = cursor.fetchone()['total_students']

        return jsonify({
            'courses': courses,
            'total_students': total_students
        })
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()