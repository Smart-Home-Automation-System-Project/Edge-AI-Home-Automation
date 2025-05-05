from flask import Flask, jsonify, render_template, request
from ..database.database import *
from ..sensor.topics import *
import json
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='config/.env')
UI_PASSWORD = os.getenv("UI_PASSWORD")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

app = Flask(__name__, template_folder='templates')
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY  # Change to something strong
jwt = JWTManager(app)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'Missing password'}), 400

    if data['password'] == UI_PASSWORD:  # Set your real password here
        token = create_access_token(identity='admin')  # Simple identity
        return jsonify({'access_token': token})
    else:
        return jsonify({'error': 'Invalid password'}), 401



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/control-panel')
def control_panel():
    return render_template('ctrlpanel.html')

@app.route('/api/modules', methods=['GET'])
@jwt_required()
def get_modules():
    modules = db_get_available_all_modules()
    return jsonify(modules)

@app.route('/api/unassigned-modules',  methods=['GET'])
@jwt_required()
def get_unassigned_modules():
    return jsonify(db_get_new_modules())

@app.route('/api/assign-module', methods=['POST'])
@jwt_required()
def assign_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'client_id' not in data or 'name' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    client_id = data['client_id']
    name = data['name']

    # Call your DB function (you need to define db_assign_module)
    result = db_assign_module(client_id, name)

    # Respond with the result
    if result > 0:
        return jsonify({'message': 'Sensor name updated successfully.'}), 200
    else:
        return jsonify({'error': 'No sensor found with the given client_id.'}), 404

@app.route('/api/replace-module', methods=['POST'])
@jwt_required()
def replace_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'new_client_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])
    new_client_id = str(data['new_client_id'])

    # Call your DB function (you need to define db_assign_module)
    result = db_replace_module(id, new_client_id)

    # Respond with the result
    if result > 0:
        return jsonify({'message': 'Sensor client_id updated successfully.'}), 200
    else:
        return jsonify({'error': 'No sensor found with the given client_id.'}), 404

@app.route('/api/delete-module', methods=['POST'])
@jwt_required()
def delete_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])

    # Call your DB function (you need to define db_assign_module)
    result = db_delete_module(id)

    # Respond with the result
    if result > 0:
        return jsonify({'message': 'Sensor client_id updated successfully.'}), 200
    else:
        return jsonify({'error': 'No sensor found with the given client_id.'}), 404

@app.route('/api/toggle-module', methods=['POST'])
@jwt_required()
def toggle_module():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'state' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])
    state = str(data['state'])

    result = 1
    client.publish(T_SENSOR_MAIN_CTRL, json.dumps({'id': id, 'state': state}))

    # Respond with the result
    if result > 0:
        return jsonify({'message': 'Module Updated.'}), 200
    else:
        return jsonify({'error': 'No sensor found with the given id.'}), 404

@app.route('/api/set-color', methods=['POST'])
@jwt_required()
def set_color():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Ensure that the data contains the expected fields
    if not data or 'id' not in data or 'irgb' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract the data from the JSON
    id = str(data['id'])
    irgb = str(data['irgb'])

    result = 1
    client.publish(T_SENSOR_MAIN_CTRL, json.dumps({'id': id, 'irgb': irgb}))

    # Respond with the result
    if result > 0:
        return jsonify({'message': 'Module Updated.'}), 200
    else:
        return jsonify({'error': 'No sensor found with the given id.'}), 404



def init_webui(_client):
    global client
    client = _client
    app.run(debug=False, host="0.0.0.0", use_reloader=False, threaded=True)