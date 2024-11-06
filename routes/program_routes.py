from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from models import db, ProgramModel, CollegeModel, StudentModel
from sqlalchemy.exc import IntegrityError

program_bp = Blueprint('program', __name__, url_prefix='/programs')

@program_bp.route('/', methods=['GET', 'POST'])
def list_programs():
    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        college_code = request.form['college']

        new_program = ProgramModel(
            course_code=course_code,
            course_name=course_name,
            college=college_code
        )

        try:
            db.session.add(new_program)
            db.session.commit()
            return redirect(url_for('program.list_programs'))
        except IntegrityError:
            db.session.rollback()
            return render_template('programs.html', 
                                error_message="Program with this course code already exists.")

    return render_template('programs.html', 
                         programs=ProgramModel.query.all(),
                         colleges=CollegeModel.query.all())

@program_bp.route('/update', methods=['POST'])
def update_program():
    original_code = request.form['originalCourseCode']
    new_code = request.form['courseCode']
    course_name = request.form['courseName']
    college_code = request.form['college']

    program = ProgramModel.query.get_or_404(original_code)
    program.course_code = new_code
    program.course_name = course_name
    program.college = college_code
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@program_bp.route('/delete/<string:course_code>', methods=['DELETE'])
def delete_program(course_code):
    program = ProgramModel.query.get_or_404(course_code)
    
    # Update students with this program
    StudentModel.query.filter_by(course=course_code).update({StudentModel.course: None})
    
    db.session.delete(program)
    db.session.commit()
    return jsonify({"message": "Program deleted successfully"})

@program_bp.route('/check_course_code', methods=['POST'])
def check_course_code():
    course_code = request.json['course_code']
    exists = ProgramModel.query.filter_by(course_code=course_code).first() is not None
    return jsonify({'exists': exists})