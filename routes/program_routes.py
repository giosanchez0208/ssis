from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

program_bp = Blueprint('program', __name__, url_prefix='/programs')

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
        college_code = request.form['college']

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO programs (course_code, course_name, college_code) VALUES (%s, %s, %s)"
                cursor.execute(sql, (course_code, course_name, college_code))
            connection.commit()
            return redirect(url_for('program.list_programs'))
        except pymysql.MySQLError as e:
            connection.rollback()
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
    college_code = request.form['college']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE programs
                SET course_code = %s, course_name = %s, college_code = %s
                WHERE course_code = %s
            """
            cursor.execute(sql, (new_code, course_name, college_code, original_code))
        connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()

@program_bp.route('/delete/<string:course_code>', methods=['DELETE'])
def delete_program(course_code):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM programs WHERE course_code = %s"
            cursor.execute(sql, (course_code,))
        connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()