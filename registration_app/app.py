from flask import Flask, jsonify,request
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Symptom
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta



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


# API resource routes go here:
# api.add_resource(UserRegistration, '/registration')

@app.route('/add_test_user', methods=['GET'])
def add_test_user():
    hashed_password = generate_password_hash("password123")
    test_user = User(
        username="testuser", 
        password=hashed_password,  # Now using hashed password
        age=30, 
        gender="M", 
        location="Test City"
    )
    db.session.add(test_user)
    db.session.commit()
    return "Test user added!"

# Route to retrieve all users
@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "age": user.age, "gender": user.gender, "location": user.location} for user in users]
    return jsonify(user_list)


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
                    'location': user.location
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
                'location': new_user.location
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# 1. POST: Create a new user
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
    return jsonify({'message': 'User created successfully'}), 201

# 2. POST: Add a symptom for a specific user
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
        return jsonify({'message': 'Symptom added successfully'}), 201
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
    return jsonify([{
        'id': symptom.id,
        'label': symptom.label,
        'description': symptom.description,
        'timestamp': symptom.timestamp
    } for symptom in symptoms])

# PUT: Update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get the data from the request
    data = request.get_json()
    user.username = data.get('username', user.username)  # If key is not provided, keep the current value
    user.password = data.get('password', user.password)  
    user.age = data.get('age', user.age)
    user.gender = data.get('gender', user.gender)
    user.location = data.get('location', user.location)

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

# DELETE: Delete an existing user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
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
            return jsonify({'message': 'Symptom not found'}), 404

        try:
            db.session.delete(symptom)
            db.session.commit()
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
            return jsonify({'message': 'Symptom updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    return inner_update_symptom()

if __name__ == '__main__':
    app.run(debug=True)