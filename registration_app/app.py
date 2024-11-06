from flask import Flask, jsonify,request
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Symptom



app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Try SQLite for now
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


api = Api(app)


# API resource routes go here:
# api.add_resource(UserRegistration, '/registration')

@app.route('/add_test_user', methods=['GET'])
def add_test_user():
    test_user = User(username="testuser", password="password123", age=30, gender="M", location="Test City")
    db.session.add(test_user)
    db.session.commit()
    return "Test user added!"

# Route to retrieve all users
@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "age": user.age, "gender": user.gender, "location": user.location} for user in users]
    return jsonify(user_list)

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
@app.route('/users/<int:user_id>/symptoms', methods=['GET'])
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
if __name__ == '__main__':
    app.run(debug=True)