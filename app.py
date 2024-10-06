from flask import Flask, render_template, request, redirect, jsonify
from models import db, StudentModel, ProgramModel, CollegeModel
from sqlalchemy.exc import IntegrityErrorfrom authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session, render_template
import os, random, string

# Config

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/ssis_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# OAuth Setup

# OAuth Setup
oauth = OAuth(app)

# Configure Google OAuth
# I WENT BACK TO THIS COMMIT AND HID THIS INFORMATION


# Google login route
@app.route('/login/google')
def google_login():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

# Google OAuth callback route
def generate_nonce(length=16):
    """Generate a random nonce."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/authorize/google')
def authorize_google():
    try:
        nonce = generate_nonce()  # Generate a nonce
        session['nonce'] = nonce  # Store the nonce in the session
        
        redirect_uri = url_for('authorize_google_callback', _external=True)
        return google.authorize_redirect(redirect_uri, nonce=nonce)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500  

@app.route('/authorize/google/callback')
def authorize_google_callback():
    try:
        # Fetch the access token
        token = google.authorize_access_token()
        if not token:
            return "Authorization failed", 400  # Handle authorization failure

        # Retrieve the nonce from the session
        nonce = session.pop('nonce', None)  # Remove it from the session

        # Parse user info using the nonce
        user_info = google.parse_id_token(token, nonce=nonce)

        # Store user info in the session
        session['user'] = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'profile': user_info.get('picture')
        }

        return redirect('/students')  # Redirect to the students page after successful login

    except Exception as e:
        return f"An error occurred: {str(e)}", 500  # Log the error and return a message


# Home route
@app.route('/')
def home():
    return render_template('home.html', user=session.get('user'))  # Pass user info to the template

# Route to logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# Routes

################# STUDENTS #################

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

################# PROGRAMS #################

@app.route('/programs', methods=['GET', 'POST'])
def programs():
    if request.method == 'POST':
        # Handle form submission to create a new program
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        college_code = request.form['college']  # This will capture the selected college code

        new_program = ProgramModel(course_code=course_code, course_name=course_name, college=college_code)

        try:
            db.session.add(new_program)
            db.session.commit()
            return redirect('/programs')
        except IntegrityError:
            db.session.rollback()
            return render_template('programs.html', error_message="Program with this course code already exists.")

    # Fetch all programs and colleges for the dropdown
    all_programs = ProgramModel.query.all()
    all_colleges = CollegeModel.query.all()

    return render_template('programs.html', programs=all_programs, colleges=all_colleges)

@app.route('/programs/<string:course_code>', methods=['GET', 'POST'])
def edit_program(course_code):
    program = ProgramModel.query.get_or_404(course_code)
    if request.method == 'POST':
        program.course_name = request.form['courseName']
        new_course_code = request.form['courseCode']
        
        if new_course_code != program.course_code:
            program.course_code = new_course_code
            # Add logic to update students with the old course code
        
        db.session.commit()
        return redirect('/programs')

    return jsonify({
        'course_code': program.course_code,
        'course_name': program.course_name,
        'college': program.college
    })

@app.route('/check_course_code', methods=['POST'])
def check_course_code():
    data = request.get_json()
    course_code = data['course_code']
    exists = ProgramModel.query.filter_by(course_code=course_code).first() is not None
    return jsonify({'exists': exists})

@app.route('/programs/delete/<string:course_code>', methods=['DELETE'])
def delete_program(course_code):
    program = ProgramModel.query.get_or_404(course_code)
    students = StudentModel.query.filter_by(course=course_code).all()

    for student in students:
        student.course = None  # Unenroll students from this course
    db.session.delete(program)
    db.session.commit()
    return jsonify({"message": "Program deleted successfully"})

@app.route('/programs/update', methods=['POST'])
def update_program():
    original_course_code = request.form['originalCourseCode']  # Get original course code
    new_course_code = request.form['courseCode']
    course_name = request.form['courseName']
    college_code = request.form['college']

    # Update logic here
    program = ProgramModel.query.filter_by(course_code=original_course_code).first()
    if program:
        program.course_code = new_course_code  # Update fields
        program.course_name = course_name
        program.college = college_code
        db.session.commit()  # Commit changes

    return jsonify({'success': True})

################# COLLEGES #################

@app.route('/colleges', methods=['GET'])
def manage_colleges():
    colleges = CollegeModel.query.all()
    programs = ProgramModel.query.all()
    return render_template('colleges.html', colleges=colleges, programs=programs)
  

@app.route('/create_college', methods=['POST'])
def create_college():
    data = request.get_json()  # Get the JSON data from the request
    college_code = data.get('college_code')
    college_name = data.get('college_name')

    if not college_name:
        return jsonify({'error': 'College name cannot be empty.'}), 400

    try:
        new_college = CollegeModel(college_code=college_code, college_name=college_name)
        db.session.add(new_college)
        db.session.commit()
        return jsonify({'success': 'College created successfully.'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'College code already exists.'}), 400

@app.route('/update_college', methods=['POST'])
def update_college():
    data = request.get_json()
    original_code = data['original_code']
    college_code = data['college_code']
    college_name = data['college_name']

    # Check if the college_code is being changed and if the new code already exists
    if original_code != college_code:
        existing_college = CollegeModel.query.filter_by(college_code=college_code).first()
        if existing_college:
            return jsonify({'message': 'College code already exists'}), 400

    # Update the college in the database
    college = CollegeModel.query.get(original_code)
    if college:
        college.college_code = college_code
        college.college_name = college_name
        db.session.commit()  # Commit the changes to the database
        return jsonify({'message': 'College updated successfully'}), 200
    else:
        return jsonify({'message': 'College not found'}), 404

@app.route('/delete_college', methods=['DELETE'])
def delete_college():
    data = request.get_json()
    college_code = data['college_code']
    
    # Find the college in the database
    college = CollegeModel.query.get(college_code)
    if college:
        db.session.delete(college)  # Delete the college from the database
        db.session.commit()  # Commit the changes
        return jsonify({'message': 'College deleted successfully'}), 200
    else:
        return jsonify({'message': 'College not found'}), 404


@app.route('/check_duplicate_college_code', methods=['POST'])
def check_duplicate_college_code():
    data = request.get_json()  # Get JSON data from the request
    college_code = data['college_code']  # Extract college_code from data
    exists = CollegeModel.query.filter_by(college_code=college_code).first() is not None  # Check if it exists
    return jsonify({'exists': exists})

if __name__ == '__main__':
    app.run(debug=True)
