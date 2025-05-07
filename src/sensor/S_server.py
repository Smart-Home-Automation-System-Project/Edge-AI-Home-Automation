from flask import Flask, jsonify
from sensor.s_module import get_module_current_power_data, get_available_all_modules_ctrl

app = Flask(__name__, template_folder='templates')

@app.route('/api/module/power', methods=['GET'])
def data():
    return jsonify(get_module_current_power_data())

@app.route('/api/module/control', methods=['GET'])
def control():
    return jsonify(get_available_all_modules_ctrl())

def init_data_server():
    app.run(debug=False, host="0.0.0.0", use_reloader=False, threaded=True, port=5001)