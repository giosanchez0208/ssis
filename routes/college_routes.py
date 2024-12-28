from flask import Blueprint, render_template, request, jsonify
import pymysql
from controllers.db_controller import (
    fetch_colleges, 
    fetch_programs, 
    insert_college, 
    update_college as update_college_db,
    delete_college as delete_college_db,
    fetch_college_info
)

college_bp = Blueprint('college', __name__, url_prefix='/colleges')

@college_bp.route('/', methods=['GET'])
def list_colleges():
    colleges = fetch_colleges()
    programs = fetch_programs()
    return render_template('colleges.html', colleges=colleges, programs=programs, active_page='colleges')

@college_bp.route('/create', methods=['POST'])
def create_college():
    data = request.get_json()
    college_code = data.get('college_code')
    college_name = data.get('college_name')

    if not college_name:
        return jsonify({'error': 'College name cannot be empty.'}), 400

    try:
        insert_college(college_code, college_name)
        return jsonify({'success': 'College created successfully.'}), 201
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400

@college_bp.route('/update', methods=['POST'])
def update_college():
    data = request.get_json()
    college_code = data.get('college_code')
    college_name = data.get('college_name')
    original_code = data.get('original_code')

    try:
        update_college_db(college_code, college_name, original_code)
        return jsonify({'success': 'College updated successfully.'}), 200
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400

@college_bp.route('/delete', methods=['DELETE'])
def delete_college():
    data = request.get_json()
    college_code = data.get('college_code')

    try:
        delete_college_db(college_code)
        return jsonify({'success': 'College deleted successfully.'}), 200
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400

@college_bp.route('/<college_code>/info', methods=['GET'])
def get_college_info(college_code):
    try:
        info = fetch_college_info(college_code)
        return jsonify(info)
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500