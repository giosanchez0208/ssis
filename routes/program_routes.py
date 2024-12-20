from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import pymysql
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

program_bp = Blueprint('program', __name__, url_prefix='/programs')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

@program_bp.route('/', methods=['GET', 'POST'])
def list_programs():
    connection = get_db_connection()
    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        college = request.form['college']

        logging.debug(f"Received form data: courseCode={course_code}, courseName={course_name}, college={college}")

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO programs (course_code, course_name, college) VALUES (%s, %s, %s)"
                cursor.execute(sql, (course_code, course_name, college))
            connection.commit()
            logging.debug("Program added successfully")
            return redirect(url_for('program.list_programs'))
        except pymysql.MySQLError as e:
            connection.rollback()
            logging.error(f"Error adding program: {e}")
            return render_template('programs.html', error_message="Program with this course code already exists.")
        finally:
            connection.close()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM programs")
            programs = cursor.fetchall()
            cursor.execute("SELECT * FROM colleges")
            colleges = cursor.fetchall()
    finally:
        connection.close()

    return render_template('programs.html', programs=programs, colleges=colleges)

@program_bp.route('/update', methods=['POST'])
def update_program():
    original_code = request.form['originalCourseCode']
    new_code = request.form['courseCode']
    course_name = request.form['courseName']
    college = request.form['college']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE programs
                SET course_code = %s, course_name = %s, college = %s
                WHERE course_code = %s
            """
            cursor.execute(sql, (new_code, course_name, college, original_code))
        connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@program_bp.route('/delete/<string:course_code>', methods=['DELETE'])
def delete_program(course_code):
    logging.debug(f"Attempting to delete program with course_code: {course_code}")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM programs WHERE course_code = %s"
            cursor.execute(sql, (course_code,))
        connection.commit()
        logging.debug(f"Program with course_code {course_code} deleted successfully")
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        connection.rollback()
        logging.error(f"Error deleting program: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()
        
@program_bp.route('/<string:course_code>/students', methods=['GET'])
def get_enrolled_students(course_code):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT s.id_num, CONCAT(UPPER(s.last_name), ', ', s.first_name) as name, s.year_level
                FROM students s
                WHERE s.course = %s
                ORDER BY s.last_name, s.first_name
            """
            cursor.execute(sql, (course_code,))
            students = cursor.fetchall()

            year_levels = {
                'first_year': sum(1 for student in students if student['year_level'] == 1),
                'second_year': sum(1 for student in students if student['year_level'] == 2),
                'third_year': sum(1 for student in students if student['year_level'] == 3),
                'fourth_year': sum(1 for student in students if student['year_level'] == 4)
            }

        return jsonify({'students': students, 'year_levels': year_levels})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)})
    finally:
        connection.close()

@program_bp.route('/check_course_code', methods=['POST'])
def check_course_code():
    data = request.get_json()
    course_code = data.get('course_code')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM programs WHERE course_code = %s"
            cursor.execute(sql, (course_code,))
            result = cursor.fetchone()
            exists = result['count'] > 0
        return jsonify({'exists': exists})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)})
    finally:
        connection.close()