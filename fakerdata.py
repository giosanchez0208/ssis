import pymysql
from faker import Faker
import random
import os

# Database connection
db = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'), 
    password=os.getenv('DB_PASSWORD', 'guerrillaRdio'),
    database=os.getenv('DB_NAME', 'ssis_db')
)
cursor = db.cursor()

# Get existing courses from database
cursor.execute("SELECT course_code FROM programs")
courses = [row[0] for row in cursor.fetchall()]

# Initialize faker with different locales
locales = ['en_US', 'en_GB', 'en_CA', 'en_AU']  
fakers = {locale: Faker(locale) for locale in locales}

def generate_id():
    prefix = "2024"
    suffix = ''.join(random.choices('0123456789', k=4))
    return f"{prefix}-{suffix}"

def generate_student():
    # Random locale selection
    locale = random.choice(locales)
    faker = fakers[locale]
    
    # Generate names
    has_two_first_names = random.choice([True, False])
    if has_two_first_names:
        first_name = f"{faker.first_name()} {faker.first_name()}"
    else:
        first_name = faker.first_name()
    last_name = faker.last_name()

    # Gender distribution
    gender = random.choices(['Male', 'Female', 'Other'], weights=[45, 45, 10])[0]
    
    return {
        'id_num': generate_id(),
        'first_name': first_name,
        'last_name': last_name,
        'course': random.choice(courses),
        'gender': gender,
        'year_level': 1,
        'profile_picture_id': None
    }

def insert_students(num_students):
    for _ in range(num_students):
        student = generate_student()
        sql = """INSERT INTO students 
                (id_num, first_name, last_name, course, gender, year_level, profile_picture_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = tuple(student.values())
        try:
            cursor.execute(sql, values)
            db.commit()
            print(f"Inserted student: {student['first_name']} {student['last_name']}")
        except pymysql.Error as e:
            print(f"Error inserting student: {e}")
            db.rollback()

# Generate students
insert_students(250)

# Close database connection
db.close()
