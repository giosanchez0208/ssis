from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import logging

import pymysql
from controllers.db_controller import fetch_colleges, fetch_programs, insert_program, update_program_db, delete_program as delete_program_db, check_course_code_exists, fetch_enrolled_students, fetch_single_program

program_bp = Blueprint('program', __name__, url_prefix='/programs')

logging.basicConfig(level=logging.DEBUG)

@program_bp.route('/', methods=['GET', 'POST'])
def list_programs():
    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        college = request.form['college']

        try:
            insert_program(course_code, course_name, college)
            return redirect(url_for('program.list_programs'))
        except pymysql.MySQLError as e:
            return render_template('programs.html', error_message="Program with this course code already exists.")

    programs = fetch_programs()
    colleges = fetch_colleges()
    return render_template('programs.html', programs=programs, colleges=colleges, active_page='programs')

@program_bp.route('/<string:course_code>', methods=['GET'])
def get_program(course_code):
    try:
        program = fetch_single_program(course_code)
        if program:
            return jsonify(program)
        else:
            return jsonify({'error': 'Program not found'}), 404
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)})

@program_bp.route('/update', methods=['POST'])
def update_program():
    original_code = request.form.get('originalCourseCode')
    new_code = request.form.get('courseCode')
    course_name = request.form.get('courseName')
    college = request.form.get('college')

    try:
        update_program_db(new_code, course_name, college, original_code)
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'error': str(e)})

@program_bp.route('/delete/<string:course_code>', methods=['DELETE'])
def delete_program_route(course_code):
    try:
        delete_program_db(course_code)
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'error': str(e)})

@program_bp.route('/<string:course_code>/students', methods=['GET'])
def get_enrolled_students(course_code):
    try:
        students = fetch_enrolled_students(course_code)
        year_levels = {
            'first_year': sum(1 for student in students if student['year_level'] == 1),
            'second_year': sum(1 for student in students if student['year_level'] == 2),
            'third_year': sum(1 for student in students if student['year_level'] == 3),
            'fourth_year': sum(1 for student in students if student['year_level'] == 4)
        }
        return jsonify({'students': students, 'year_levels': year_levels})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)})

@program_bp.route('/check_course_code', methods=['POST'])
def check_course_code():
    data = request.get_json()
    course_code = data.get('course_code')

    try:
        exists = check_course_code_exists(course_code)
        return jsonify({'exists': exists})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)})