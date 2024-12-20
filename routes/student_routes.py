import pymysql
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
import os
from urllib.parse import urlparse
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
        
        
student_bp = Blueprint('student', __name__, url_prefix='/students')

def list_students():
    conn = get_db_connection()
    if conn is None:
        return render_template('students.html', error_message="Failed to connect to the database.")
    
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        cur.execute("SELECT course_code, course_name FROM programs")
        programs = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('students.html', students=students, programs=programs)
    except Exception as e:
        current_app.logger.error(f"Database operation failed: {e}")
        return render_template('students.html', error_message=f"An error occurred: {str(e)}")


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
                conn = get_db_connection()
                cur = conn.cursor(pymysql.cursors.DictCursor)
                cur.execute("SELECT * FROM students")
                students = cur.fetchall()
                cur.execute("SELECT course_code, course_name FROM programs")
                programs = cur.fetchall()
                cur.close()
                conn.close()
                return render_template('students.html', students=students, programs=programs, error_message="Please fill out all required fields.")

            if gender == "Custom":
                custom_gender = request.form.get('customGender')
                gender = custom_gender if custom_gender else gender

            conn = get_db_connection()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            
            try:
                cur.execute("""
                    INSERT INTO students 
                    (id_num, first_name, last_name, course, year_level, gender, profile_picture_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (id_num, first_name, last_name, course, year_level, gender, profile_picture_id))
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('student.list_students'))
            
            except pymysql.err.IntegrityError:
                conn.rollback()
                cur.close()
                conn.close()
                return render_template('students.html', error_message="ID Number already exists.")

        except Exception as e:
            return render_template('students.html', error_message=f"An error occurred: {str(e)}")

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.execute("SELECT course_code, course_name FROM programs")
    programs = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('students.html', students=students, programs=programs)

@student_bp.route('/get_programs', methods=['GET'])
def get_programs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_code, course_name FROM programs")
    programs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(programs)

@student_bp.route('/edit/<string:id_num>', methods=['GET', 'POST'])
def edit(id_num):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        try:
            form_data = request.form
            cur.execute("""
                UPDATE students 
                SET first_name = %s, 
                    last_name = %s, 
                    course = %s, 
                    year_level = %s, 
                    gender = %s, 
                    profile_picture_id = %s
                WHERE id_num = %s
            """, (
                form_data['firstName'], 
                form_data['lastName'], 
                form_data.get('course'),
                form_data['year'], 
                form_data['gender'], 
                form_data.get('profile_picture_id'),
                id_num
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Student updated successfully"})
        
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": f"Update failed: {str(e)}"})

    cur.execute("SELECT * FROM students WHERE id_num = %s", (id_num,))
    student = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify(student)

@student_bp.route('/delete/<string:id_num>')
def delete(id_num):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM students WHERE id_num = %s", (id_num,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('student.list_students'))
    
    except Exception as e:
        cur.close()
        conn.close()
        return "Error"

@student_bp.route('/check_id', methods=['POST'])
def check_id():
    id_num = request.json['id_num']
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT EXISTS(SELECT 1 FROM students WHERE id_num = %s)", (id_num,))
    exists = cur.fetchone()['exists']
    
    cur.close()
    conn.close()
    
    return jsonify({'exists': exists})

@student_bp.route('/data', methods=['POST'])
def get_student_data():
    # pagination
    start = int(request.form['start'])
    length = int(request.form['length'])
    # filter results
    search_value = request.form.get('search[value]', '')
    # sorting
    order_column = request.form.get('order[0][column]', '0')
    order_dir = request.form.get('order[0][dir]', 'asc')
    # filter by course
    course_filter = request.form.get('courseFilter', '')

    conn = get_db_connection()
    cur = conn.cursor()

    # base query
    query = """
        SELECT * FROM students 
        WHERE 1=1
    """
    params = []

    # course query filter
    if course_filter:
        query += " AND course = %s"
        params.append(course_filter)

    # search value query filter
    if search_value:
        search_term = f"%{search_value}%"
        query += """ 
            AND (
                id_num LIKE %s OR 
                first_name LIKE %s OR 
                last_name LIKE %s OR 
                course LIKE %s OR 
                gender LIKE %s
            )
        """
        params.extend([search_term] * 5)

    # order by
    columns = [None, 'id_num', 'last_name', 'year_level', 'course', 'gender']
    if order_column and int(order_column) < len(columns) and columns[int(order_column)] is not None:
        sort_column = columns[int(order_column)]
        query += f" ORDER BY {sort_column} {order_dir.upper()}"
        
    
    cur.execute("SELECT COUNT(*) FROM students")
    total_records = cur.fetchone()['COUNT(*)']

    count_query = query.replace("*", "COUNT(*)")
    cur.execute(count_query, params)
    filtered_records = cur.fetchone()['COUNT(*)']

    query += " LIMIT %s OFFSET %s"
    params.extend([length, start])

    cur.execute(query, params)
    students = cur.fetchall()

    cur.close()
    conn.close()
    data = {
        'draw': int(request.form['draw']),
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': students
    }
    
    return jsonify(data)