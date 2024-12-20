import os
import mysql.connector
import pymysql

# Database connection
db = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'), 
    password=os.getenv('DB_PASSWORD', 'guerrillaRdio'),
    database=os.getenv('DB_NAME', 'ssis_db')
)
cursor = db.cursor()

# College data
colleges = [
    ('CASS', 'COLLEGE OF ARTS AND SOCIAL SCIENCES'),
    ('CEBA', 'COLLEGE OF ECONOMICS AND BUSINESS ADMINISTRATION'),
    ('CSM', 'COLLEGE OF SCIENCE AND MATHEMATICS'),
    ('CCS', 'COLLEGE OF COMPUTER STUDIES'),
    ('CHS', 'COLLEGE OF HEALTH SCIENCES'),
    ('COE', 'COLLEGE OF ENGINEERING'),
    ('CED', 'COLLEGE OF EDUCATION')
]

# Program data organized by college
programs = [
    # CASS Programs
    ('BAELS', 'Bachelor of Arts in English Language Studies', 'CASS'),
    ('BAFil', 'Bachelor of Arts in Filipino', 'CASS'),
    ('BAHis', 'Bachelor of Arts in History', 'CASS'),
    ('BAPan', 'Bachelor of Arts in Panitikan', 'CASS'),
    ('BAPolSci', 'Bachelor of Arts in Political Science', 'CASS'),
    ('BASocio', 'Bachelor of Arts in Sociology', 'CASS'),
    ('BSPsych', 'Bachelor of Science in Psychology', 'CASS'),
    ('BSPhilo', 'Bachelor of Philosophy - Applied Ethics', 'CASS'),
    
    # CEBA Programs
    ('BSAcc', 'Bachelor of Science in Accountancy', 'CEBA'),
    ('BSEcon', 'Bachelor of Science in Economics', 'CEBA'),
    ('BSEntrep', 'Bachelor of Science in Entrepreneurship', 'CEBA'),
    ('BSHM', 'Bachelor of Science in Hospitality Management', 'CEBA'),
    ('BSBABE', 'Bachelor of Science in Business Administration - Business Economics', 'CEBA'),
    ('BSBAMM', 'Bachelor of Science in Business Administration - Marketing Management', 'CEBA'),
    
    # CSM Programs
    ('BSBIO-AB', 'Bachelor of Science in Biology (Animal Biology)', 'CSM'),
    ('BSBIO-PB', 'Bachelor of Science in Biology (Plant Biology)', 'CSM'),
    ('BSBIO-BD', 'Bachelor of Science in Biology (Biodiversity)', 'CSM'),
    ('BSBIO-MB', 'Bachelor of Science in Biology (Microbiology)', 'CSM'),
    ('BSChem', 'Bachelor of Science in Chemistry', 'CSM'),
    ('BSMarineBio', 'Bachelor of Science in Marine Biology', 'CSM'),
    ('BSMath', 'Bachelor of Science in Mathematics', 'CSM'),
    ('BSPhys', 'Bachelor of Science in Physics', 'CSM'),
    ('BSStat', 'Bachelor of Science in Statistics', 'CSM'),
    
    # CCS Programs
    ('BSCA', 'Bachelor of Science in Computer Applications', 'CCS'),
    ('BSCS', 'Bachelor of Science in Computer Science', 'CCS'),
    ('BSIS', 'Bachelor of Science in Information Systems', 'CCS'),
    ('BSIT', 'Bachelor of Science in Information Technology', 'CCS'),
    
    # CHS Programs
    ('BSN', 'Bachelor of Science in Nursing', 'CHS'),
    
    # COE Programs
    ('BSCerE', 'Bachelor of Science in Ceramics Engineering', 'COE'),
    ('BSChE', 'Bachelor of Science in Chemical Engineering', 'COE'),
    ('BSCE', 'Bachelor of Science in Civil Engineering', 'COE'),
    ('BSEcE', 'Bachelor of Science in Electrical Engineering', 'COE'),
    ('BSEE', 'Bachelor of Science in Electronics Engineering', 'COE'),
    ('BSEnviE', 'Bachelor of Science in Environmental Engineering', 'COE'),
    ('BSIAM', 'Bachelor of Science in Industrial Automation and Mechatronics', 'COE'),
    ('BSME', 'Bachelor of Science in Mechanical Engineering', 'COE'),
    ('BSMetE', 'Bachelor of Science in Metallurgical Engineering', 'COE'),
    ('BSMinE', 'Bachelor of Science in Mining Engineering', 'COE'),
    ('BET-CHET', 'Bachelor of Engineering Technology - Chemical Engineering Technology', 'COE'),
    ('BET-CET', 'Bachelor of Engineering Technology - Civil Engineering Technology', 'COE'),
    ('BET-ECET', 'Bachelor of Engineering Technology - Electrical Engineering Technology', 'COE'),
    ('BET-EET', 'Bachelor of Engineering Technology - Electronics Engineering Technology', 'COE'),
    ('BET-MET', 'Bachelor of Engineering Technology - Mechanical Engineering Technology', 'COE'),
    ('BET-MM', 'Bachelor of Engineering Technology - Metallurgical and Materials', 'COE'),
    ('BET-PET', 'Bachelor of Engineering Technology - Processing Engineering Technology', 'COE'),
    
    # CED Programs
    ('BEEd-LE', 'Bachelor of Elementary Education - Language Education', 'CED'),
    ('BEEd-SM', 'Bachelor of Elementary Education - Science and Mathematics', 'CED'),
    ('BSEd-Bio', 'Bachelor of Secondary Education - Biology', 'CED'),
    ('BSEd-Chem', 'Bachelor of Secondary Education - Chemistry', 'CED'),
    ('BSEd-Math', 'Bachelor of Secondary Education - Mathematics', 'CED'),
    ('BSED-Phys', 'Bachelor of Secondary Education - Physics', 'CED'),
    ('BSED-Fil', 'Bachelor of Secondary Education - Filipino', 'CED'),
    ('BTVTED-DT', 'Bachelor of Technical-Vocational Teacher Education - Drafting Technology', 'CED'),
    ('BTLEd-HomeEc', 'Bachelor of Technology and Livelihood Education - Home Economics', 'CED'),
    ('BTLEd-IA', 'Bachelor of Technology and Livelihood Education - Industrial Arts', 'CED'),
    ('BPEd', 'Bachelor of Physical Education', 'CED')
]

def insert_demo_data():
    try:
        # Use the existing db connection from the top of the file
        global db, cursor

        # Insert colleges
        for college_code, college_name in colleges:
            try:
                cursor.execute(
                    "INSERT INTO colleges (college_code, college_name) VALUES (%s, %s)",
                    (college_code, college_name)
                )
                print(f"Added college: {college_code}")
            except pymysql.err.IntegrityError:
                print(f"College {college_code} already exists, skipping...")
                
        # Insert programs
        for course_code, course_name, college in programs:
            try:
                cursor.execute(
                    "INSERT INTO programs (course_code, course_name, college) VALUES (%s, %s, %s)",
                    (course_code, course_name, college)
                )
                print(f"Added program: {course_code}")
            except pymysql.err.IntegrityError:
                print(f"Program {course_code} already exists, skipping...")
        
        # Commit the changes
        db.commit()
        print("\nDemo data insertion completed successfully!")
        
    except pymysql.Error as err:
        print(f"Error: {err}")
        db.rollback()  # Rollback in case of error
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        db.rollback()

if __name__ == "__main__":
    insert_demo_data()