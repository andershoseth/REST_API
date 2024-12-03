from flask import Flask, jsonify, request, url_for
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Symptom, ActivityLog
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from collections import Counter
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db.init_app(app)
with app.app_context():
    db.create_all()

jwt = JWTManager(app)
api = Api(app)



# Route to retrieve all users
@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "age": user.age,
            "gender": user.gender,
            "location": user.location,
            "links": {
                "self": url_for('get_user', user_id=user.id, _external=True),
                "symptoms": url_for('get_user_symptoms', user_id=user.id, _external=True)
            }
        }
        user_list.append(user_dict)
    return jsonify(user_list)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_dict = {
        "id": user.id,
        "username": user.username,
        "age": user.age,
        "gender": user.gender,
        "location": user.location,
        "links": {
            "self": url_for('get_user', user_id=user.id, _external=True),
            "symptoms": url_for('get_user_symptoms', user_id=user.id, _external=True),
            "update": url_for('update_user', user_id=user.id, _external=True),
            "delete": url_for('delete_user', user_id=user.id, _external=True)
        }
    }
    return jsonify(user_dict)

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'age': user.age,
                    'gender': user.gender,
                    'location': user.location,
                    'links': {
                        'self': url_for('get_user', user_id=user.id, _external=True),
                        'symptoms': url_for('get_user_symptoms', user_id=user.id, _external=True)
                    }
                }
            }), 200

        return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400

        # Create new user with hashed password
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            password=hashed_password,
            age=data.get('age'),
            gender=data.get('gender'),
            location=data.get('location')
        )

        db.session.add(new_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': access_token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'age': new_user.age,
                'gender': new_user.gender,
                'location': new_user.location,
                'links': {
                    'self': url_for('get_user', user_id=new_user.id, _external=True),
                    'symptoms': url_for('get_user_symptoms', user_id=new_user.id, _external=True)
                }
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/create_user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        password=data['password'],  
        age=data.get('age'),
        gender=data.get('gender'),
        location=data.get('location')
    )
    db.session.add(new_user)
    db.session.commit()
   
    log_user_activity("Create User", 201)
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>/symptoms', methods=['POST'])
def add_symptom(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    new_symptom = Symptom(
        userid=user_id,
        label=data['label'],
        description=data['description']
    )

    try:
        db.session.add(new_symptom)
        db.session.commit()
        log_user_activity("Add Symptom", 201)

        symptom_dict = {
            'id': new_symptom.id,
            'label': new_symptom.label,
            'description': new_symptom.description,
            'timestamp': new_symptom.timestamp.isoformat(),
            'links': {
                'self': url_for('get_symptom', user_id=user_id, symptom_id=new_symptom.id, _external=True),
                'user': url_for('get_user', user_id=user_id, _external=True),
                'update': url_for('update_symptom', user_id=user_id, symptom_id=new_symptom.id, _external=True),
                'delete': url_for('delete_symptom', user_id=user_id, symptom_id=new_symptom.id, _external=True)
            }
        }

        return jsonify(symptom_dict), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# GET: Get all symptoms for a user
@app.route('/users/<int:user_id>/symptoms', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user_symptoms(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    symptoms = Symptom.query.filter_by(userid=user_id).all()
    log_user_activity("Get User Symptoms", 200)

    symptoms_list = []
    for symptom in symptoms:
        symptom_dict = {
            'id': symptom.id,
            'label': symptom.label,
            'description': symptom.description,
            'timestamp': symptom.timestamp.isoformat(),
            'links': {
                'self': url_for('get_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
                'user': url_for('get_user', user_id=user_id, _external=True),
                'update': url_for('update_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
                'delete': url_for('delete_symptom', user_id=user_id, symptom_id=symptom.id, _external=True)
            }
        }
        symptoms_list.append(symptom_dict)

    return jsonify(symptoms_list)

@app.route('/users/<int:user_id>/symptoms/<int:symptom_id>', methods=['GET'])
def get_symptom(user_id, symptom_id):
    symptom = Symptom.query.filter_by(userid=user_id, id=symptom_id).first()
    if not symptom:
        return jsonify({'message': 'Symptom not found'}), 404

    symptom_dict = {
        'id': symptom.id,
        'label': symptom.label,
        'description': symptom.description,
        'timestamp': symptom.timestamp.isoformat(),
        'links': {
            'self': url_for('get_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
            'user': url_for('get_user', user_id=user_id, _external=True),
            'update': url_for('update_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
            'delete': url_for('delete_symptom', user_id=user_id, symptom_id=symptom.id, _external=True)
        }
    }
    return jsonify(symptom_dict)

# PUT: Update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get the data from the request
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.password = data.get('password', user.password)  
    user.age = data.get('age', user.age)
    user.gender = data.get('gender', user.gender)
    user.location = data.get('location', user.location)

    db.session.commit()
    log_user_activity("Update User", 200)

    user_dict = {
        "id": user.id,
        "username": user.username,
        "age": user.age,
        "gender": user.gender,
        "location": user.location,
        "links": {
            "self": url_for('get_user', user_id=user.id, _external=True),
            "symptoms": url_for('get_user_symptoms', user_id=user.id, _external=True),
            "update": url_for('update_user', user_id=user.id, _external=True),
            "delete": url_for('delete_user', user_id=user.id, _external=True)
        }
    }

    return jsonify({'message': 'User updated successfully', 'user': user_dict}), 200

# DELETE: Delete an existing user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    log_user_activity("Delete User", 200)

    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/users/<int:user_id>/symptoms/<int:symptom_id>', methods=['DELETE', 'OPTIONS'])
def delete_symptom(user_id, symptom_id):
    if request.method == 'OPTIONS':
        return '', 200  # Allow the OPTIONS request to pass through

    @jwt_required()
    def inner_delete_symptom():
        if get_jwt_identity() != user_id:
            return jsonify({'message': 'Unauthorized access'}), 403

        symptom = Symptom.query.filter_by(userid=user_id, id=symptom_id).first()
        if not symptom:
            log_user_activity("Delete Symptom - Not Found", 404)
            return jsonify({'message': 'Symptom not found'}), 404

        try:
            db.session.delete(symptom)
            db.session.commit()
       
            log_user_activity("Delete Symptom", 200)
            return jsonify({'message': 'Symptom deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return inner_delete_symptom()

@app.route('/users/<int:user_id>/symptoms/<int:symptom_id>', methods=['PUT', 'OPTIONS'])
def update_symptom(user_id, symptom_id):
    if request.method == 'OPTIONS':
        return '', 200  # Allow the OPTIONS request to pass through

    @jwt_required()
    def inner_update_symptom():
        if get_jwt_identity() != user_id:
            return jsonify({'message': 'Unauthorized access'}), 403

        symptom = Symptom.query.filter_by(userid=user_id, id=symptom_id).first()
        if not symptom:
            return jsonify({'message': 'Symptom not found'}), 404

        data = request.get_json()
        symptom.label = data.get('label', symptom.label)
        symptom.description = data.get('description', symptom.description)

        try:
            db.session.commit()
            log_user_activity("Update Symptom", 200)

            symptom_dict = {
                'id': symptom.id,
                'label': symptom.label,
                'description': symptom.description,
                'timestamp': symptom.timestamp.isoformat(),
                'links': {
                    'self': url_for('get_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
                    'user': url_for('get_user', user_id=user_id, _external=True),
                    'update': url_for('update_symptom', user_id=user_id, symptom_id=symptom.id, _external=True),
                    'delete': url_for('delete_symptom', user_id=user_id, symptom_id=symptom.id, _external=True)
                }
            }

            return jsonify({'message': 'Symptom updated successfully', 'symptom': symptom_dict}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return inner_update_symptom()

def log_user_activity(action, status_code):
    """Logs the user's activity to the ActivityLog table."""
    try:
        user_id = get_jwt_identity()  # Get logged-in user ID from JWT
        if user_id:
            new_log = ActivityLog(
                user_id=user_id,
                action=action,  
                endpoint=request.path,  
                method=request.method,  
                ip_address=request.remote_addr,  
                timestamp=datetime.utcnow(),  
                status_code=status_code  
            )
            db.session.add(new_log)
            db.session.commit()
    except Exception as e:
        # Error handling/logging
        print(f"Failed to log activity: {str(e)}")

# Shows the activity logs for a specific user
@app.route('/activity_logs/<int:user_id>', methods=['GET'])
def get_activity_logs(user_id):
    """Retrieve activity logs for a specific user without authentication."""
    logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).all()

    if not logs:
        return jsonify({'message': f'No activity logs found for user ID {user_id}'}), 404

    return jsonify([{
        'action': log.action,
        'endpoint': log.endpoint,
        'method': log.method,
        'ip_address': log.ip_address,
        'timestamp': log.timestamp.isoformat(),
        'status_code': log.status_code
    } for log in logs]), 200

# Pattern recognition, finds the most common combinations of symptoms
@app.route('/symptoms/patterns', methods=['GET'])
def identify_common_symptom_patterns():
    users = User.query.all()
    symptom_combinations = []

    for user in users:
        user_symptoms = Symptom.query.filter_by(userid=user.id).all()
        symptom_labels = [symptom.label for symptom in user_symptoms]

        if len(symptom_labels) > 1:
            sorted_labels = tuple(sorted(symptom_labels))
            symptom_combinations.append(sorted_labels)

    combination_counts = Counter(symptom_combinations)
    most_common_patterns = combination_counts.most_common(5)

    patterns = []
    for combo, count in most_common_patterns:
        patterns.append({
            'symptoms': list(combo),
            'count': count
        })

    return jsonify({'most_common_patterns': patterns}), 200

@app.route('/fill_database', methods=['GET'])
def fill_database():
    try:
        # Delete previous data to avoid duplicates
        db.session.query(Symptom).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Define some possible usernames, locations, symptoms, and genders
        male_names = ['Bob', 'Charlie', 'David', 'Frank', 'Hank', 'Jack', 'Leo', 'Oscar', 'Paul', 'Quinn', 'Steve', 'Victor', 'Xander', 'Zack', 'Oliver', 'Liam', 'Noah', 'Lucas', 'Ethan', 'James', 'Benjamin', 'Alexander', 'William', 'Henry', 'Sebastian']
        female_names = ['Alice', 'Eva', 'Grace', 'Ivy', 'Karen', 'Mona', 'Nina', 'Rachel', 'Tina', 'Uma', 'Wendy', 'Yara', 'Sophia', 'Emma', 'Ava', 'Mia', 'Amelia', 'Isabella', 'Harper', 'Evelyn', 'Abigail', 'Emily', 'Ella', 'Chloe']
        locations = ['Oslo', 'Bergen', 'Trondheim', 'Stavanger', 'Kristiansand', 'Drammen', 'Tromsø', 'Bodø']
        genders = ['M', 'F']
        symptom_labels = [
            'fever', 'cough', 'headache', 'fatigue', 'sore throat', 'muscle pain', 'nausea', 'shortness of breath',
            'runny nose', 'loss of taste', 'loss of smell', 'diarrhea'
        ]

        # Add 100 test users with random attributes
        users = []
        for i in range(100):
            gender = random.choice(genders)
            if gender == 'M':
                username = f"{random.choice(male_names)}_{i}"
            else:
                username = f"{random.choice(female_names)}_{i}"

            user = User(
                username=username,
                password=generate_password_hash('password123'),
                age=random.randint(18, 65),
                gender=gender,
                location=random.choice(locations)
            )
            users.append(user)

        # Add users to the database
        db.session.add_all(users)
        db.session.commit()

        # Add symptoms for each user
        symptoms = []
        for user in users:
            num_symptoms = random.randint(1, 3)
            user_symptom_labels = random.sample(symptom_labels, num_symptoms)

            for index, label in enumerate(user_symptom_labels):
                description = f'{label} experienced by {user.username} on day {index + 1}'
                symptom = Symptom(
                    userid=user.id,
                    label=label,
                    description=description
                )
                symptoms.append(symptom)

        # Add symptoms to the database
        db.session.add_all(symptoms)
        db.session.commit()

        return jsonify({'message': 'Database filled with 100 users and sample data successfully!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
