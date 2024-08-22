from flask import Flask, request, jsonify
from newsLetter.newsletter import signup_newsletter

app = Flask(__name__)

@app.route('/newsletter/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    preferences = data.get('preferences', [])

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        # TODO: If user already exists in spreadsheet, return 409

        # Save the user to the database
        signup_newsletter(name, email, preferences)
        return jsonify({'message': 'User signed up successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# TODO: Unsubscribe feature
if __name__ == '__main__':
    app.run()