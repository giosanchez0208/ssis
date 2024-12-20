import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
from urllib.parse import urlparse
import pymysql
import os

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

program_bp = Blueprint('program', __name__, url_prefix='/programs')

@program_bp.route('/', methods=['GET', 'POST'])
def list_programs():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        college_code = request.form['college']

        try:
            sql = "INSERT INTO programs (course_code, course_name, college) VALUES (%s, %s, %s)"
            cursor.execute(sql, (course_code, course_name, college_code))
            conn.commit()
            return redirect(url_for('program.list_programs'))
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.execute("SELECT * FROM programs")
            programs = cursor.fetchall()
            cursor.execute("SELECT * FROM colleges")
            colleges = cursor.fetchall()
            return render_template('programs.html', 
                                   programs=programs, 
                                   colleges=colleges, 
                                   error_message="Program with this course code already exists.")
        finally:
            cursor.close()
            conn.close()

    cursor.execute("SELECT * FROM programs")
    programs = cursor.fetchall()
    cursor.execute("SELECT * FROM colleges")
    colleges = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('programs.html', 
                         programs=programs, 
                         colleges=colleges)

@program_bp.route('/update', methods=['POST'])
def update_program():
    conn = get_db_connection()
    cursor = conn.cursor()

    original_code = request.form['originalCourseCode']
    new_code = request.form['courseCode']
    course_name = request.form['courseName']
    college_code = request.form['college']

    try:
        update_sql = "UPDATE programs SET course_code = %s, course_name = %s, college = %s WHERE course_code = %s"
        cursor.execute(update_sql, (new_code, course_name, college_code, original_code))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@program_bp.route('/delete/<string:course_code>', methods=['DELETE'])
def delete_program(course_code):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        update_students_sql = "UPDATE students SET course = NULL WHERE course = %s"
        cursor.execute(update_students_sql, (course_code,))

        delete_program_sql = "DELETE FROM programs WHERE course_code = %s"
        cursor.execute(delete_program_sql, (course_code,))
        conn.commit()
        return jsonify({"message": "Program deleted successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Delete failed: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@program_bp.route('/check_course_code', methods=['POST'])
def check_course_code():
    course_code = request.json['course_code']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = "SELECT EXISTS(SELECT 1 FROM programs WHERE course_code = %s)"
        cursor.execute(sql, (course_code,))
        exists = cursor.fetchone()[0]
        return jsonify({'exists': exists})
    finally:
        cursor.close()
        conn.close()