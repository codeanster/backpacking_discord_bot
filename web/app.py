import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS  # This is required for handling CORS if needed
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes, adjust if needed

# Configuration for file uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory storage for demonstration purposes
trip_status = {
    'status': 'not on a trip',
    'location': 'unknown',
    'return_date': 'unknown',
    'photo_url': ''
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, output_path, quality=85):
    with Image.open(image_path) as img:
        img.save(output_path, "JPEG", quality=quality)

@app.route('/')
def index():
    return render_template('index.html', trip_status=trip_status)

@app.route('/update_status', methods=['POST'])
def update_status():
    # Handling JSON data for AJAX
    data = request.get_json()  # Using get_json() to properly parse incoming JSON data
    if data:
        trip_status['status'] = data.get('status', trip_status['status'])
        trip_status['location'] = data.get('location', trip_status['location'])
        trip_status['return_date'] = data.get('return_date', trip_status['return_date'])
        return jsonify(trip_status)
    return jsonify({"error": "No data provided"}), 400

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        # Compress the image
        compress_image(temp_path, file_path)

        # Remove the temporary file
        os.remove(temp_path)

        trip_status['photo_url'] = f'/uploads/{filename}'
        return jsonify(trip_status)
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(trip_status)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)
