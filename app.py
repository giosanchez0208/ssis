from flask import Flask, render_template, request, redirect
from models import db, StudentModel
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
    
def create():
    if request.method == 'GET':
        return render_template('')
# Database



# Routes
import os

@app.route('/list_students')
def list_students():
    try:
        students = StudentModel.query.all()
        if not students:
            return "No students found in the database."

        # Generate a response string with all student details
        student_list = ""
        for student in students:
            student_list += f"ID: {student.id_num}, Name: {student.first_name} {student.last_name}, " \
                            f"Gender: {student.gender}, Year Level: {student.year_level}, Course: {student.course}<br>"

        return student_list
    except Exception as e:
        return f"An error occurred: {str(e)}"


        # Add the new student to the session and commit to the database
        db.session.add(new_student)
        db.session.commit()

        return f"Inserted student: {new_student.first_name} {new_student.last_name} ({new_student.id_num})"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/colleges')
def colleges():
    return render_template('colleges.html')

if __name__ == '__main__':
    app.run(debug=True)