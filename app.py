from flask import Flask, render_template, request, redirect, jsonify
from models import db, StudentModel, ProgramModel
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

@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        try:
            id_num = f"{request.form['idPart1']}-{request.form['idPart2']}"
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            course = request.form.get('course', None)
            year_level = request.form['year']
            gender = request.form['gender']
            
            if gender == "Custom":
                custom_gender = request.form.get('customGender', None)
                if custom_gender:
                    gender = custom_gender

            new_student = StudentModel(
                id_num=id_num,
                first_name=first_name,
                last_name=last_name,
                course=course,
                gender=gender,
                year_level=year_level
            )

            db.session.add(new_student)
            db.session.commit()

            return redirect('/students')
        
        except IntegrityError:
            db.session.rollback() 
            all_students = StudentModel.query.all()
            all_programs = ProgramModel.query.all()
            return render_template('students.html', 
                                   students=all_students,
                                   programs=all_programs,
                                   error_message="ID Number already exists.")

    all_students = StudentModel.query.all()
    all_programs = ProgramModel.query.all()
    return render_template('students.html', students=all_students, programs=all_programs)

@app.route('/check_id', methods=['POST'])
def check_id():
    id_num = request.json['id_num']
    exists = StudentModel.query.filter_by(id_num=id_num).first() is not None
    return jsonify({'exists': exists})

@app.route('/colleges')
def colleges():
    return render_template('colleges.html')

if __name__ == '__main__':
    app.run(debug=True)