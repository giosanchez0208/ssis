from flask import Flask, render_template, request, redirect, jsonify
from models import db, StudentModel, ProgramModel, CollegeModel
from sqlalchemy.exc import IntegrityError
import os

# Config

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/ssis_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def home():
    return render_template('home.html')

# students

@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        try:
            id_num = request.form['idNumber']
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            course = request.form['course']
            year_level = request.form['year']
            gender = request.form['gender']
            
            if not id_num or not first_name or not last_name or not year_level or not gender:
                return render_template('students.html', 
                                       students=StudentModel.query.all(),
                                       programs=ProgramModel.query.all(),
                                       error_message="Please fill out all required fields.")

            if gender == "Custom":
                custom_gender = request.form.get('customGender', None)
                if custom_gender:
                    gender = custom_gender
                    
            if course=="" or not course:
                course = None

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
            except IntegrityError:
                db.session.rollback()
                return render_template('students.html', 
                                       students=StudentModel.query.all(),
                                       programs=ProgramModel.query.all(),
                                       error_message="ID Number already exists.")

            return redirect('/students')

        except Exception as e:
            db.session.rollback()
            return render_template('students.html', 
                                   students=StudentModel.query.all(),
                                   programs=ProgramModel.query.all(),
                                   error_message=f"An error occurred: {str(e)}")

    all_students = StudentModel.query.all()
    all_programs = ProgramModel.query.all()
    return render_template('students.html', students=all_students, programs=all_programs)
from flask import jsonify
@app.route('/edit/<string:id_num>', methods=['GET', 'POST'])
def edit(id_num):
    student = StudentModel.query.get_or_404(id_num)
    if request.method == 'POST':
        try:
            student.first_name = request.form['firstName']
            student.last_name = request.form['lastName']
            student.course = request.form['course'] or None  # Set to None if empty string
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
            print(f"Error updating student: {str(e)}")  # Print the error to console
            return jsonify({"success": False, "message": f"There was an issue updating the student: {str(e)}"})
    elif request.method == 'GET':
        return jsonify({
            'id_num': student.id_num,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'course': student.course,
            'year_level': student.year_level,
            'gender': student.gender
        })

@app.route('/delete/<string:id_num>')
def delete(id_num):
    student_to_delete = StudentModel.query.get_or_404(id_num)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        return redirect('/students')
    except:
        return "There was a problem deleting that student."

@app.route('/check_id', methods=['POST'])
def check_id():
    id_num = request.json['id_num']
    exists = StudentModel.query.filter_by(id_num=id_num).first() is not None
    return jsonify({'exists': exists})

# programs

@app.route('/programs', methods=['GET', 'POST'])
def programs():
    if request.method == 'POST':
        try:
            course_code = request.form['courseCode']
            course_name = request.form['courseName']
            college = request.form['college']

            if not course_code or not course_name or not college:
                return render_template('programs.html', 
                                       programs=ProgramModel.query.all(),
                                       colleges=CollegeModel.query.all(),
                                       error_message="Please fill out all required fields.")

            new_program = ProgramModel(
                course_code=course_code,
                course_name=course_name,
                college=college
            )

            db.session.add(new_program)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_template('programs.html', 
                                       programs=ProgramModel.query.all(),
                                       colleges=CollegeModel.query.all(),
                                       error_message="Course Code already exists.")

            return redirect('/programs')

        except Exception as e:
            db.session.rollback()
            return render_template('programs.html', 
                                   programs=ProgramModel.query.all(),
                                   colleges=CollegeModel.query.all(),
                                   error_message=f"An error occurred: {str(e)}")

    all_programs = ProgramModel.query.all()
    all_colleges = CollegeModel.query.all()
    return render_template('programs.html', programs=all_programs, colleges=all_colleges)

@app.route('/edit_program/<string:course_code>', methods=['GET', 'POST'])
def edit_program(course_code):
    program = ProgramModel.query.get_or_404(course_code)
    if request.method == 'POST':
        try:
            if 'courseCode' in request.form and request.form['courseCode'] != course_code:
                # If course code is changed, create a new program and delete the old one
                new_program = ProgramModel(
                    course_code=request.form['courseCode'],
                    course_name=request.form['courseName'],
                    college=request.form['college']
                )
                db.session.add(new_program)
                db.session.delete(program)
            else:
                program.course_name = request.form['courseName']
                if 'college' in request.form:
                    program.college = request.form['college']

            db.session.commit()
            return jsonify({"success": True, "message": "Program updated successfully"})
        except IntegrityError:
            db.session.rollback()
            return jsonify({"success": False, "message": "Course Code already exists"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"There was an issue updating the program: {str(e)}"})
    elif request.method == 'GET':
        return jsonify({
            'course_code': program.course_code,
            'course_name': program.course_name,
            'college': program.college
        })

@app.route('/delete_program/<string:course_code>')
def delete_program(course_code):
    program_to_delete = ProgramModel.query.get_or_404(course_code)
    try:
        db.session.delete(program_to_delete)
        db.session.commit()
        return redirect('/programs')
    except:
        return "There was a problem deleting that program."

@app.route('/check_course_code', methods=['POST'])
def check_course_code():
    course_code = request.json['course_code']
    exists = ProgramModel.query.filter_by(course_code=course_code).first() is not None
    return jsonify({'exists': exists})

if __name__ == '__main__':
    app.run(debug=True)