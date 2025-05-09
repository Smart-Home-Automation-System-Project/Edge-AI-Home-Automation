from flask import Flask, jsonify, render_template, request, make_response
from flask import request, redirect, url_for
from database.database import *
from sensor.topics import *
import json
from dotenv import load_dotenv
import os
import jwt
from functools import wraps
import subprocess

load_dotenv(dotenv_path='config/.env')
UI_PASSWORD = os.getenv("UI_PASSWORD")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
IP_SAS_SYSTEM = os.getenv("IP_SAS_SYSTEM")
IP_ECO_SYSTEM = os.getenv("IP_ECO_SYSTEM")
JWT_SESSION_TIME = 15

app = Flask(__name__, template_folder='templates')

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        url = request.url
        if 'api' in str(url):
            if not token:
                return redirect(url_for('login_page'), code=401)

            try:
                jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                print("[DEBUG] Token expired")
                return redirect(url_for('login_page'), code=401)
            except jwt.InvalidTokenError:
                print("[DEBUG] Invalid token")
                return redirect(url_for('login_page'), code=401)
        else:
            if not token:
                return redirect(url_for('login_page'), code=307)

            try:
                jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                print("[DEBUG] Token expired")
                return redirect(url_for('login_page'), code=307)
            except jwt.InvalidTokenError:
                print("[DEBUG] Invalid token")
                return redirect(url_for('login_page'), code=307)

        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def login_page1():
    return render_template('login.html')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'Missing password'}), 400

    if data['password'] == UI_PASSWORD:
        token = jwt.encode({'user': 'admin', 'exp': datetime.utcnow() + timedelta(minutes=JWT_SESSION_TIME)}, JWT_SECRET_KEY, algorithm='HS256')
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('token', token, httponly=True, samesite='Strict')
        return response
    else:
        return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/session/extend', methods=['POST'])
@jwt_required
def extend_session():
    token = jwt.encode({'user': 'admin', 'exp': datetime.utcnow() + timedelta(minutes=JWT_SESSION_TIME)}, JWT_SECRET_KEY, algorithm='HS256')
    response = make_response(jsonify({'message': 'Login successful'}))
    response.set_cookie('token', token, httponly=True, samesite='Strict')
    return response


@app.route('/dashboard')
@jwt_required
def dashboard():
    return render_template('dashboard.html')



@app.route('/control-panel')
@jwt_required
def control_panel():
    return render_template('ctrlpanel.html')

@app.route('/api/modules', methods=['GET'])
@jwt_required
def get_modules():
    try:
        modules = db_get_available_all_modules()
        return jsonify(modules)
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

@app.route('/api/unassigned-modules',  methods=['GET'])
@jwt_required
def get_unassigned_modules():
    try:
        modules = db_get_new_modules()
        return jsonify(modules)
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

@app.route('/api/assign-module', methods=['POST'])
@jwt_required
def assign_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'client_id' not in data or 'name' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    client_id = data['client_id']
    name = data['name']

    try:
        result = db_assign_module(client_id, name)
        # Respond with the result
        if result > 0:
            return jsonify({'message': 'Sensor name updated successfully.'}), 200
        else:
            return jsonify({'error': 'No sensor found with the given client_id.'}), 404
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

@app.route('/api/replace-module', methods=['POST'])
@jwt_required
def replace_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'new_client_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])
    new_client_id = str(data['new_client_id'])

    try:
        result = db_replace_module(id, new_client_id)

        # Respond with the result
        if result > 0:
            return jsonify({'message': 'Sensor client_id updated successfully.'}), 200
        else:
            return jsonify({'error': 'No sensor found with the given client_id.'}), 404
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500
    
    

@app.route('/api/delete-module', methods=['POST'])
@jwt_required
def delete_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])

    try:
        result = db_delete_module(id)

        # Respond with the result
        if result > 0:
            return jsonify({'message': 'Sensor client_id updated successfully.'}), 200
        else:
            return jsonify({'error': 'No sensor found with the given client_id.'}), 404
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

    

@app.route('/api/toggle-module', methods=['POST'])
@jwt_required
def toggle_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'state' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    id = str(data['id'])
    # Extract the data from the JSON
    try:
        name = db_get_client_name(id)
        state = str(data['state'])

        result = 1
        client.publish(T_SENSOR_MAIN_CTRL, json.dumps({'name': name, 'state': state}))

        # Respond with the result
        if result > 0:
            return jsonify({'message': 'Module Updated.'}), 200
        else:
            return jsonify({'error': 'No sensor found with the given id.'}), 404
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

    

@app.route('/api/set-color', methods=['POST'])
@jwt_required
def set_color():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'irgb' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])
    irgb = str(data['irgb'])

    try:
        name = db_get_client_name(id)
        result = 1
        client.publish(T_SENSOR_MAIN_CTRL, json.dumps({'name': name, 'irgb': irgb}))

        # Respond with the result
        if result > 0:
            return jsonify({'message': 'Module Updated.'}), 200
        else:
            return jsonify({'error': 'No sensor found with the given id.'}), 404
    except DatabaseError:
        return jsonify({"error": "DatabaseError: Please reinstall database"}), 500

    



@app.route('/camera')
@jwt_required
def live_cam():
    return render_template('camera.html')

@app.route('/api/camera_url')
@jwt_required
def get_camera_url():
    return {'url': f'http://{IP_SAS_SYSTEM}/video_feed'}


@app.route('/api/power_url')
@jwt_required
def get_page_url():
    return {'url': f'http://{IP_ECO_SYSTEM}/power'}



@app.route('/recovery/main-ctrl')
@jwt_required
def recovery():
    return render_template('recovery.html')

@app.route('/api/restore/db', methods=['POST'])
@jwt_required
def restoreDB():
    # Use absolute paths to ensure correct file locations
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'backup_restore_script.py')
    firebase_credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'firebase_credentials.json')
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'database.db')

    # Make sure the directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Check if script exists
    if not os.path.exists(script_path):
        return jsonify({'error': f'Script not found at: {script_path}'}), 500
        
    # Check if credentials exist
    if not os.path.exists(firebase_credentials_path):
        return jsonify({'error': f'Firebase credentials not found at: {firebase_credentials_path}'}), 500
    
    # Build the command - using the latest backup (no backup-id specified)
    command = [
        "python", 
        script_path, 
        'restore', 
        '--cred-path', firebase_credentials_path, 
        '--target-path', output_path,
    ]
    
    try:
        # Print the command for debugging
        print(f"Executing: {' '.join(command)}")
        
        # Run with timeout to prevent hanging
        result = subprocess.run(
            command, 
            check=True, 
            text=True, 
            capture_output=True,
            timeout=300  # 5 minute timeout
        )
        
        # Log the output for debugging
        print(f"Command output: {result.stdout}")
        
        return jsonify({
            'msg': 'DB restore success',
            'details': result.stdout
        }), 200
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with return code {e.returncode}: {e.stderr}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500
        
    except subprocess.TimeoutExpired as e:
        error_msg = f"Command timed out after {e.timeout} seconds"
        print(error_msg)
        return jsonify({'error': error_msg}), 504
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500





def init_webui(_client):
    global client
    client = _client
    app.run(debug=False, host="0.0.0.0", use_reloader=False, threaded=True, port=80)