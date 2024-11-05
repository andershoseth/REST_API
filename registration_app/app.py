from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager




app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Try SQLite for now
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


api = Api(app)


# API resource routes go here:
# api.add_resource(UserRegistration, '/registration')