import random
from faker import Faker
from models import db
from config import create_app
from models import StudentModel

# Configuration values for the course and gender
COURSES = [
    "BAELS", "BAFil", "BAHis", "BAPan", "BAPolSci", "BASocio", "BEEd-LE", "BEEd-SM", "BET-CET", "BET-CHET",
    "BET-ECET", "BET-EET", "BET-MET", "BET-MM", "BET-PET", "BPEd", "BSAcc", "BSBABE", "BSBAMM", "BSBIO (Animal Bi)",
    "BSBIO (Biodivers)", "BSBIO (Microbiol)", "BSBIO (Plant Bio)", "BSCA", "BSCE", "BSCerE", "BSChE", "BSChem",
    "BSCS", "BSEcE", "BSEcon", "BSEd-Bio", "BSEd-Chem", "BSEd-Fil", "BSEd-Math", "BSEd-Phys", "BSEE", "BSEntrep",
    "BSEnviE", "BSHM", "BSIAM", "BSIS", "BSIT", "BSMarineBio", "BSMath", "BSME", "BSMetE", "BSMinE", "BSN",
    "BSPhilo", "BSPhys", "BSPsych", "BSStat", "BTLEd-HomeEc", "BTLEd-IA", "BTVTED-DT"
]

GENDERS = ["Male", "Female", "Other"]  # with 'other' appearing less frequently

# Reduced list of locales with Latin-based languages only
locales = [
    'en_US', 'es_ES', 'fr_FR', 'pt_PT', 'it_IT', 'de_DE', 'en_GB', 'pl_PL', 'nl_NL', 'sv_SE', 
    'da_DK', 'no_NO', 'fi_FI', 'cs_CZ', 'ro_RO', 'hu_HU', 'sk_SK', 'hr_HR', 'lt_LT', 'lv_LV', 
    'et_EE'
]

def generate_random_student(firstFourDigits, customYearLevel):
    """
    Generate a random student with a specified course code prefix and year level.
    """
    # Choose a random locale for this student
    locale = random.choice(locales)  # Randomly choose a locale for diversity
    fake = Faker(locale)  # Faker instance with the selected locale

    # Random data generation
    first_name = fake.first_name()

    # 50% chance of adding a second first name
    if random.random() < 0.5:
        second_first_name = fake.first_name()
        first_name += " " + second_first_name

    # 2% chance of adding a third first name
    if random.random() < 0.02:
        third_first_name = fake.first_name()
        first_name += " " + third_first_name
    
    last_name = fake.last_name()
    gender = random.choices(GENDERS, weights=[0.48, 0.48, 0.04])[0]  # 'other' has a smaller weight
    year_level = customYearLevel  # As per the specification
    course = random.choice(COURSES) if random.random() < 0.8 else None  # 80% chance for a course to be set

    # Build the id_num in the format ####-####, using the firstFourDigits
    id_num = f"{firstFourDigits}-{random.randint(1000, 9999)}"
    
    # Create the student instance
    student = StudentModel(
        id_num=id_num,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        year_level=year_level,
        course=course,
        profile_picture_id=None  # Keep the profile_picture_id as None
    )
    
    return student

def add_student_to_db(student):
    """
    Add a student to the database with error handling.
    """
    try:
        db.session.add(student)
        db.session.commit()
        print(f"Added student: {student.first_name} {student.last_name} ({student.id_num})")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Failed to add student {student.first_name} {student.last_name} ({student.id_num}): {str(e)}")

def generate_and_add_students(num_students, firstFourDigits, customYearLevel):
    """
    Generate and add multiple students to the database.
    """
    for _ in range(num_students):
        student = generate_random_student(firstFourDigits, customYearLevel)
        add_student_to_db(student)

if __name__ == "__main__":
    # Define your firstFourDigits and customYearLevel here
    firstFourDigits = "2024"  # Example for course code prefix
    customYearLevel = 1  # Example for Year Level
    
    # Ensure you have a Flask app context
    app = create_app()  # Assuming create_app is the function that initializes your Flask app

    with app.app_context():
        # Generate and add 1000 students to the database
        generate_and_add_students(1000, firstFourDigits, customYearLevel)
