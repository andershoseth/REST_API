from flask import Flask, jsonify
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



if __name__ == '__main__':
    app.run(debug=True)