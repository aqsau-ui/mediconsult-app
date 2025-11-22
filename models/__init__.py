# models/__init__.py
from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, name, email, password, user_type, phone=None, specialization=None, 
                 age=None, gender=None, allergies=None, medical_history=None):
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type
        self.phone = phone
        self.specialization = specialization
        self.age = age
        self.gender = gender
        self.allergies = allergies or []
        self.medical_history = medical_history or []
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "user_type": self.user_type,
            "phone": self.phone,
            "specialization": self.specialization,
            "age": self.age,
            "gender": self.gender,
            "allergies": self.allergies,
            "medical_history": self.medical_history,
            "created_at": self.created_at
        }

class Consultation:
    def __init__(self, patient_id, doctor_id, symptoms, medical_history=None, 
                 allergies=None, status="pending", diagnosis=None, prescription=None, 
                 lab_requests=None, consultation_notes=None, lab_reports=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.symptoms = symptoms
        self.medical_history = medical_history or []
        self.allergies = allergies or []
        self.status = status  # pending, in_progress, completed
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.lab_requests = lab_requests or []
        self.consultation_notes = consultation_notes
        self.lab_reports = lab_reports or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "symptoms": self.symptoms,
            "medical_history": self.medical_history,
            "allergies": self.allergies,
            "status": self.status,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "lab_requests": self.lab_requests,
            "consultation_notes": self.consultation_notes,
            "lab_reports": self.lab_reports,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class LabReport:
    def __init__(self, consultation_id, patient_id, doctor_id, report_type, 
                 report_data, file_path=None, notes=None):
        self.consultation_id = consultation_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.report_type = report_type
        self.report_data = report_data
        self.file_path = file_path
        self.notes = notes
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "consultation_id": self.consultation_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "report_type": self.report_type,
            "report_data": self.report_data,
            "file_path": self.file_path,
            "notes": self.notes,
            "created_at": self.created_at
        }