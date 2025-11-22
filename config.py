# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "mediconsult"

# Collections
USERS_COLLECTION = "users"
CONSULTATIONS_COLLECTION = "consultations"
LAB_REPORTS_COLLECTION = "lab_reports"

# User Types
USER_TYPE_PATIENT = "patient"
USER_TYPE_DOCTOR = "doctor"
USER_TYPE_ADMIN = "admin"

# Specializations
SPECIALIZATIONS = [
    "Cardiologist",
    "Dermatologist",
    "Neurologist",
    "Orthopedic",
    "Pediatrician",
    "Psychiatrist",
    "General Physician"
]