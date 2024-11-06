from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from models import db, StudentModel, ProgramModel
from sqlalchemy.exc import IntegrityError

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/', methods=['GET', 'POST'])
def list_students():
    if request.method == 'POST':
        try:
            id_num = request.form['idNumber']
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            course = request.form['course']
            year_level = request.form['year']
            gender = request.form['gender']
            
            if not all([id_num, first_name, last_name, year_level, gender]):
                return render_template('students.html', 
                                    students=StudentModel.query.all(),
                                    programs=ProgramModel.query.all(),
                                    error_message="Please fill out all required fields.")

            if gender == "Custom":
                custom_gender = request.form.get('customGender')
                gender = custom_gender if custom_gender else gender
                    
            course = course if course else None

            new_student = StudentModel(
                id_num=id_num,
                first_name=first_name,
                last_name=last_name,
                course=course,
                gender=gender,
                year_level=year_level
            )

            db.session.add(new_student)
            try:
                db.session.commit()
                return redirect(url_for('student.list_students'))
            except IntegrityError:
                db.session.rollback()
                return render_template('students.html', 
                                    students=StudentModel.query.all(),
                                    programs=ProgramModel.query.all(),
                                    error_message="ID Number already exists.")

        except Exception as e:
            db.session.rollback()
            return render_template('students.html', 
                                students=StudentModel.query.all(),
                                programs=ProgramModel.query.all(),
                                error_message=f"An error occurred: {str(e)}")

    return render_template('students.html', 
                         students=StudentModel.query.all(), 
                         programs=ProgramModel.query.all())

# Add this new route for getting programs
@student_bp.route('/get_programs', methods=['GET'])
def get_programs():
    programs = ProgramModel.query.all()
    return jsonify([{
        'course_code': program.course_code,
        'course_name': program.course_name
    } for program in programs])

@student_bp.route('/edit/<string:id_num>', methods=['GET', 'POST'])
def edit(id_num):
    student = StudentModel.query.get_or_404(id_num)
    if request.method == 'POST':
        try:
            form_data = request.form
            student.first_name = form_data['firstName']
            student.last_name = form_data['lastName']
            student.course = form_data['course'] or None
            student.year_level = form_data['year']
            student.gender = form_data['gender']
            
            if student.gender == "Custom":
                custom_gender = form_data.get('customGender')
                if custom_gender:
                    student.gender = custom_gender

            db.session.commit()
            return jsonify({"success": True, "message": "Student updated successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Update failed: {str(e)}"})
    
    return jsonify({
        'id_num': student.id_num,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'course': student.course,
        'year_level': student.year_level,
        'gender': student.gender
    })

@student_bp.route('/delete/<string:id_num>')
def delete(id_num):
    student = StudentModel.query.get_or_404(id_num)
    try:
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('student.list_students'))
    except Exception as e:
        return f"Error deleting student: {str(e)}"

@student_bp.route('/check_id', methods=['POST'])
def check_id():
    id_num = request.json['id_num']
    exists = StudentModel.query.filter_by(id_num=id_num).first() is not None
    return jsonify({'exists': exists})

# Flask route to fetch student data
@student_bp.route('/data', methods=['POST'])
def get_student_data():
    # Get the paging and sorting parameters from the request
    start = int(request.form['start'])
    length = int(request.form['length'])
    search_value = request.form.get('search[value]', '')
    order_column = int(request.form.get('order[0][column]', 0))
    order_dir = request.form.get('order[0][dir]', 'asc')

    # Base query
    query = StudentModel.query

    # Apply search filter if search value exists
    if search_value:
        search_term = f"%{search_value}%"
        query = query.filter(
            db.or_(
                StudentModel.id_num.like(search_term),
                StudentModel.first_name.like(search_term),
                StudentModel.last_name.like(search_term),
                StudentModel.course.like(search_term),
                StudentModel.gender.like(search_term)
            )
        )

    # Define column mapping for sorting
    column_mapping = {
        0: None,  # Profile picture column - not sortable
        1: StudentModel.id_num,
        2: StudentModel.last_name,  # Sort by last name for the full name column
        3: StudentModel.year_level,
        4: StudentModel.course,
        5: StudentModel.gender,
        6: None,  # Edit button - not sortable
        7: None   # Delete button - not sortable
    }

    # Apply sorting
    if order_column in column_mapping and column_mapping[order_column] is not None:
        sort_column = column_mapping[order_column]
        if order_dir == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # Get total records before pagination
    total_records = StudentModel.query.count()
    filtered_records = query.count()

    # Apply pagination
    students = query.offset(start).limit(length).all()

    # Prepare the response data
    data = {
        'draw': int(request.form['draw']),
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': [
            {
                'id_num': student.id_num,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'year_level': student.year_level,
                'course': student.course,
                'gender': student.gender
            } for student in students
        ]
    }
    
    return jsonify(data)