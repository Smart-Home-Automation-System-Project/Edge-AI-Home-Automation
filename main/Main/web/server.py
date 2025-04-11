from flask import Flask, jsonify, render_template
from database.database import get_all_modules

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/modules')
def get_modules():
    modules = get_all_modules()
    return jsonify(modules)




def init_webui():
    app.run(debug=True, host="0.0.0.0")