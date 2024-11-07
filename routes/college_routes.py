from flask import Blueprint, render_template, request, jsonify, url_for
from models import db, CollegeModel, ProgramModel
from sqlalchemy.exc import IntegrityError

college_bp = Blueprint('college', __name__, url_prefix='/colleges')

@college_bp.route('/', methods=['GET'])
def list_colleges():
    return render_template('colleges.html',
                         colleges=CollegeModel.query.all(),
                         programs=ProgramModel.query.all())

@college_bp.route('/create', methods=['POST'])
def create_college():
    data = request.get_json()
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

@college_bp.route('/update', methods=['POST'])
def update_college():
    data = request.get_json()
    original_code = data['original_code']
    college_code = data['college_code']
    college_name = data['college_name']

    if original_code != college_code:
        existing = CollegeModel.query.filter_by(college_code=college_code).first()
        if existing:
            return jsonify({'message': 'College code already exists'}), 400

    college = CollegeModel.query.get_or_404(original_code)
    college.college_code = college_code
    college.college_name = college_name
    
    try:
        db.session.commit()
        return jsonify({'message': 'College updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Update failed: {str(e)}'}), 500

@college_bp.route('/delete', methods=['DELETE'])
def delete_college():
    college_code = request.json['college_code']
    college = CollegeModel.query.get_or_404(college_code)
    
    try:
        db.session.delete(college)
        db.session.commit()
        return jsonify({'message': 'College deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Delete failed: {str(e)}'}), 500

@college_bp.route('/check_code', methods=['POST'])
def check_duplicate_college_code():
    college_code = request.json['college_code']
    exists = CollegeModel.query.filter_by(college_code=college_code).first() is not None
    return jsonify({'exists': exists})