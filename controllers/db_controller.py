import pymysql
import os
from urllib.parse import urlparse
from flask import current_app

# database connection
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

# student methods
def fetch_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return students

def insert_student(id_num, first_name, last_name, course, year_level, gender, profile_picture_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students 
            (id_num, first_name, last_name, course, year_level, gender, profile_picture_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_num, first_name, last_name, course, year_level, gender, profile_picture_id))
        conn.commit()
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def update_student(id_num, first_name, last_name, course, year_level, gender, profile_picture_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE students 
            SET first_name = %s, 
                last_name = %s, 
                course = %s, 
                year_level = %s, 
                gender = %s, 
                profile_picture_id = %s
            WHERE id_num = %s
        """, (first_name, last_name, course, year_level, gender, profile_picture_id, id_num))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def delete_student(id_num):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE id_num = %s", (id_num,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def check_student_id_exists(id_num):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM students WHERE id_num = %s) as exists_check", (id_num,))
    exists = cur.fetchone()['exists_check']
    cur.close()
    conn.close()
    return exists

def fetch_student_data(query, params):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_total_records():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    total_records = cur.fetchone()['COUNT(*)']
    cur.close()
    conn.close()
    return total_records

def fetch_filtered_records(query, params):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    filtered_records = cur.fetchone()['COUNT(*)']
    cur.close()
    conn.close()
    return filtered_records

def get_students_with_filters(start, length, search_value, order_column, order_dir, course_filter):
    query = """
        SELECT * FROM students s
        LEFT JOIN programs p ON s.course = p.course_code
        LEFT JOIN colleges c ON p.college = c.college_code
        WHERE 1=1
    """
    params = []

    if course_filter:
        query += " AND s.course = %s"
        params.append(course_filter)

    if search_value:
        search_term = f"%{search_value}%"
        query += """ 
            AND (
                s.id_num LIKE %s OR 
                s.first_name LIKE %s OR 
                s.last_name LIKE %s OR 
                s.course LIKE %s OR 
                s.gender LIKE %s OR
                p.course_code LIKE %s OR
                p.course_name LIKE %s OR
                c.college_code LIKE %s OR
                c.college_name LIKE %s
            )
        """
        params.extend([search_term] * 9)

    columns = [None, 's.id_num', 's.last_name', 's.year_level', 's.course', 's.gender']
    if order_column and int(order_column) < len(columns) and columns[int(order_column)] is not None:
        sort_column = columns[int(order_column)]
        query += f" ORDER BY {sort_column} {order_dir.upper()}"

    count_query = query.replace("*", "COUNT(*)")
    filtered_records = fetch_filtered_records(count_query, params)

    query += " LIMIT %s OFFSET %s"
    params.extend([length, start])

    students = fetch_student_data(query, params)
    return filtered_records, students

def fetch_single_student(id_num):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE id_num = %s", (id_num,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    return student

# student profile picture methods
def get_student_profile_picture_id(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT profile_picture_id FROM students WHERE id_num = %s', (student_id,))
        result = cur.fetchone()
        return result['profile_picture_id'] if result else None
    finally:
        cur.close()
        conn.close()

def update_profile_picture_id(student_id, picture_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE students SET profile_picture_id = %s WHERE id_num = %s', 
                   (picture_id, student_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def remove_profile_picture(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE students SET profile_picture_id = NULL WHERE id_num = %s', (student_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# program methods
def fetch_programs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_code, course_name, college FROM programs")
    programs = cur.fetchall()
    cur.close()
    conn.close()
    return programs

def insert_program(course_code, course_name, college):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO programs (course_code, course_name, college) VALUES (%s, %s, %s)", (course_code, course_name, college))
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def update_program(course_code, course_name, college, original_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE programs
            SET course_code = %s, course_name = %s, college = %s
            WHERE course_code = %s
        """, (course_code, course_name, college, original_code))
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def update_program_db(new_code, course_name, college, original_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE programs
            SET course_code = %s, course_name = %s, college = %s
            WHERE course_code = %s
        """, (new_code, course_name, college, original_code))
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def delete_program(course_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM programs WHERE course_code = %s", (course_code,))
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def check_course_code_exists(course_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM programs WHERE course_code = %s", (course_code,))
    result = cur.fetchone()
    exists = result['count'] > 0
    cur.close()
    conn.close()
    return exists

def fetch_enrolled_students(course_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id_num, CONCAT(UPPER(s.last_name), ', ', s.first_name) as name, s.year_level
        FROM students s
        WHERE s.course = %s
        ORDER BY s.last_name, s.first_name
    """, (course_code,))
    students = cur.fetchall()
    cur.close()
    conn.close()
    return students

def fetch_single_program(course_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_code, course_name, college FROM programs WHERE course_code = %s", (course_code,))
    program = cur.fetchone()
    cur.close()
    conn.close()
    return program

# college methods
def fetch_colleges():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM colleges")
    colleges = cur.fetchall()
    cur.close()
    conn.close()
    return colleges

def insert_college(college_code, college_name):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO colleges (college_code, college_name) VALUES (%s, %s)", (college_code, college_name))
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def update_college(college_code, college_name, original_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE colleges
            SET college_code = %s, college_name = %s
            WHERE college_code = %s
        """, (college_code, college_name, original_code))
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def delete_college(college_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        current_app.logger.debug(f"Attempting to delete college with code: {college_code}")  # Debug log
        cur.execute("DELETE FROM colleges WHERE college_code = %s", (college_code,))
        conn.commit()
        current_app.logger.debug(f"College with code {college_code} deleted successfully")  # Debug log
    except pymysql.MySQLError as e:
        conn.rollback()
        current_app.logger.error(f"Error deleting college: {str(e)}")  # Debug log
        raise
    finally:
        cur.close()
        conn.close()

def fetch_college_info(college_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.course_code, p.course_name, COUNT(s.id_num) AS student_count
        FROM programs p
        LEFT JOIN students s ON p.course_code = s.course
        WHERE p.college = %s
        GROUP BY p.course_code, p.course_name
    """, (college_code,))
    courses = cur.fetchall()

    cur.execute("""
        SELECT COUNT(s.id_num) AS total_students
        FROM students s
        JOIN programs p ON s.course = p.course_code
        WHERE p.college = %s
    """, (college_code,))
    total_students = cur.fetchone()['total_students']

    cur.close()
    conn.close()
    return {'courses': courses, 'total_students': total_students}
