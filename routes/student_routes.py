from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
import pymysql
from controllers.db_controller import fetch_students, fetch_programs, insert_student, update_student, delete_student, check_student_id_exists, fetch_student_data, fetch_total_records, fetch_filtered_records, get_students_with_filters, fetch_single_student

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/', methods=['GET', 'POST'])
def list_students():
    student_id = request.args.get('id')
    show_modal = False
    
    if student_id:
        show_modal = True
        
    if request.method == 'POST':
        try:
            id_num = request.form['idNumber']
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            course = request.form.get('course')
            year_level = request.form['year']
            gender = request.form['gender']
            profile_picture_id = request.form.get('profile_picture_id')

            if not all([id_num, first_name, last_name, year_level, gender]):
                students = fetch_students()
                programs = fetch_programs()
                return render_template('students.html', students=students, programs=programs, error_message="Please fill out all required fields.")

            if gender == "Custom":
                custom_gender = request.form.get('customGender')
                gender = custom_gender if custom_gender else gender

            try:
                insert_student(id_num, first_name, last_name, course, year_level, gender, profile_picture_id)
                return redirect(url_for('student.list_students'))
            
            except pymysql.err.IntegrityError:
                return render_template('students.html', error_message="ID Number already exists.")

        except Exception as e:
            return render_template('students.html', error_message=f"An error occurred: {str(e)}")

    students = fetch_students()
    programs = fetch_programs()
    return render_template('students.html', students=students, programs=programs, show_modal=show_modal)

@student_bp.route('/get_programs', methods=['GET'])
def get_programs():
    programs = fetch_programs()
    return jsonify(programs)

@student_bp.route('/edit/<string:id_num>', methods=['GET', 'POST'])
def edit(id_num):
    if request.method == 'POST':
        try:
            form_data = request.form
            update_student(id_num, form_data['firstName'], form_data['lastName'], form_data.get('course'), form_data['year'], form_data['gender'], form_data.get('profile_picture_id'))
            return jsonify({"success": True, "message": "Student updated successfully"})
        
        except Exception as e:
            return jsonify({"success": False, "message": f"Update failed: {str(e)}"})

    student = fetch_single_student(id_num)
    if student:
        return jsonify(student)
    else:
        return jsonify({"success": False, "message": "Student not found"})

@student_bp.route('/delete/<string:id_num>')
def delete(id_num):
    try:
        delete_student(id_num)
        return redirect(url_for('student.list_students'))
    
    except Exception as e:
        return "Error"

@student_bp.route('/check_id', methods=['POST'])
def check_id():
    id_num = request.json['id_num']
    exists = check_student_id_exists(id_num)
    return jsonify({'exists': exists})

@student_bp.route('/data', methods=['POST'])
def get_student_data():
    start = int(request.form['start'])
    length = int(request.form['length'])
    search_value = request.form.get('search[value]', '')
    order_column = request.form.get('order[0][column]', '0')
    order_dir = request.form.get('order[0][dir]', 'asc')
    course_filter = request.form.get('courseFilter', '')

    total_records = fetch_total_records()
    filtered_records, students = get_students_with_filters(start, length, search_value, order_column, order_dir, course_filter)

    data = {
        'draw': int(request.form['draw']),
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': students
    }
    
    return jsonify(data)