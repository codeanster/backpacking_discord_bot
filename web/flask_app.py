import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from PIL import Image
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

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

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, output_path, quality=20):
    with Image.open(image_path) as img:
        img.save(output_path, "JPEG", quality=quality)

@app.route('/')
def index():
    return render_template('index.html', trip_status=trip_status)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    if data:
        for key in ['status', 'location', 'return_date']:
            if key in data:
                trip_status[key] = data[key]
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

@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    photo_url = trip_status.get('photo_url', '')
    if photo_url:
        filename = os.path.basename(photo_url)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        trip_status['photo_url'] = ''
        return jsonify({"message": "Photo deleted", "photo_url": ''})
    return jsonify({"error": "No photo to delete"}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(trip_status)

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Process the incoming message and extract lat and lon from the URL found in the message."""
    # Get the message the user sent to our Twilio number
    body = request.values.get('Body', None)
    logging.info(f'Message Body: {body}')

    # Respond with a message
    resp = MessagingResponse()

    #send response
    resp.message("Failed to retrieve coordinates. Please check the URL.")

    return str(resp)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)
