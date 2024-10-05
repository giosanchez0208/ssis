from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class StudentModel(db.Model):
    __tablename__ = "students"

    id_num = db.Column(db.String(16), primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(16), nullable=True)
    gender = db.Column(db.Text, nullable=False)
    year_level = db.Column(db.Integer, nullable=False)

    def __init__(self, id_num, first_name, last_name, gender, year_level, course=None):
        self.id_num = id_num
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.year_level = year_level
        self.course = course
        
        def __repr__(self):
            return f"{self.first_name}:{self.last_name}"
class ProgramModel(db.Model):
    __tablename__ = "programs"

    course_code = db.Column(db.String(16), primary_key=True)  
    college = db.Column(db.String(16), nullable=False)  
    course_name = db.Column(db.Text, nullable=False) 

    def __init__(self, course_code, college, course_name):
        self.course_code = course_code
        self.college = college
        self.course_name = course_name

        def __repr__(self):
            return f"{self.course_code} - {self.course_name}"
