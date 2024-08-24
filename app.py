from flask import Flask, request, jsonify
from newsLetter.newsletter import signup_newsletter, email_exists, google_sheets_service, unsubscribe_user, unsubscribe_user_uuid

app = Flask(__name__)

@app.route('/newsletter/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    preferences = data.get('preferences', [])
    service = google_sheets_service()

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        # Check if the email already exists
        if email_exists(service, email):
            return jsonify({'error': 'Email already exists'}), 409

        # Save the user to the database
        signup_newsletter(service, name, email, preferences)
        return jsonify({'message': 'User signed up successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/newsletter/unsubscribe', methods=['POST'])
def unsubscribe_by_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Initialize Google Sheets service
        service = google_sheets_service()

        # Unsubscribe the user by marking the 5th column as "True"
        if unsubscribe_user(service, email):
            return jsonify({'message': 'User unsubscribed successfully'}), 200
        else:
            return jsonify({'error': 'Email not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/newsletter/unsubscribe/<uuid>', methods=['GET'])
def unsubscribe_by_uuid(uuid):
    try:
        # Initialize Google Sheets service
        service = google_sheets_service()

        # Unsubscribe the user by marking the 5th column as "True"
        if unsubscribe_user_uuid(service, uuid):
            return jsonify({'message': 'User unsubscribed successfully'}), 200
        else:
            return jsonify({'error': 'Invalid unsubscription link'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()