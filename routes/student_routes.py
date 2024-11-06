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

@student_bp.route('/edit/<string:id_num>', methods=['GET', 'POST'])
def edit(id_num):
    student = StudentModel.query.get_or_404(id_num)
    if request.method == 'POST':
        try:
            student.first_name = request.form['firstName']
            student.last_name = request.form['lastName']
            student.course = request.form['course'] or None
            student.year_level = request.form['year']
            student.gender = request.form['gender']
            
            if student.gender == "Custom":
                custom_gender = request.form.get('customGender')
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
