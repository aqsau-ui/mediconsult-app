# utils/__init__.py
import bcrypt
import streamlit as st
from database.connection import db
from config import USERS_COLLECTION
from bson import ObjectId

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(name, email, password, user_type, **kwargs):
    users_collection = db.get_collection(USERS_COLLECTION)
    
    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return False, "User already exists"
    
    # Create new user
    hashed_password = hash_password(password)
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "user_type": user_type,
        **kwargs
    }
    
    result = users_collection.insert_one(user_data)
    return True, "User registered successfully"

def authenticate_user(email, password):
    users_collection = db.get_collection(USERS_COLLECTION)
    user = users_collection.find_one({"email": email})
    
    if user and verify_password(password, user["password"]):
        return True, user
    return False, None

def get_user_by_id(user_id):
    users_collection = db.get_collection(USERS_COLLECTION)
    return users_collection.find_one({"_id": user_id})

def get_doctors_by_specialization(specialization=None):
    users_collection = db.get_collection(USERS_COLLECTION)
    query = {"user_type": "doctor"}
    if specialization:
        query["specialization"] = specialization
    return list(users_collection.find(query))

def get_all_patients():
    users_collection = db.get_collection(USERS_COLLECTION)
    return list(users_collection.find({"user_type": "patient"}))