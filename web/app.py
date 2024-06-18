from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for demonstration purposes
trip_status = {
    'status': 'not on a trip',
    'location': 'unknown',
    'return_date': 'unknown'
}

@app.route('/')
def index():
    return render_template('index.html', trip_status=trip_status)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    trip_status['status'] = data['status']
    trip_status['location'] = data['location']
    trip_status['return_date'] = data['return_date']
    return jsonify(trip_status)

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(trip_status)

if __name__ == '__main__':
    app.run(debug=True, port=5000)