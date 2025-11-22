# pages/patient_dashboard.py
import streamlit as st
from datetime import datetime
from database.connection import db
from models import Consultation
from config import CONSULTATIONS_COLLECTION, SPECIALIZATIONS
from utils import get_doctors_by_specialization, get_user_by_id

def patient_dashboard():
    st.title("👨‍💼 Patient Dashboard")
    
    user_id = st.session_state.user_id
    user_type = st.session_state.user_type
    
    if user_type != "patient":
        st.error("Access denied. Patients only.")
        return
    
    # Sidebar navigation
    menu = ["New Consultation", "Re-consultation", "Consultation History"]
    choice = st.sidebar.selectbox("Navigation", menu)
    
    consultations_collection = db.get_collection(CONSULTATIONS_COLLECTION)
    
    if choice == "New Consultation":
        st.header("🆕 First-time Consultation")
        
        with st.form("new_consultation"):
            st.subheader("Personal Information")
            age = st.number_input("Age", min_value=1, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            allergies = st.text_area("Allergies (comma separated)")
            medical_history = st.text_area("Medical History")
            
            st.subheader("Medical Information")
            symptoms = st.text_area("Current Symptoms", placeholder="Describe your symptoms in detail...")
            
            st.subheader("Select Specialist")
            specialization = st.selectbox("Specialization", SPECIALIZATIONS)
            
            # Get doctors by specialization
            doctors = get_doctors_by_specialization(specialization)
            doctor_options = {f"{doc['name']} ({doc['specialization']})": doc["_id"] for doc in doctors}
            
            if doctor_options:
                selected_doctor = st.selectbox("Available Doctors", list(doctor_options.keys()))
                doctor_id = doctor_options[selected_doctor]
            else:
                st.warning("No doctors available for this specialization")
                doctor_id = None
            
            st.subheader("Upload Lab Reports (Optional)")
            uploaded_files = st.file_uploader("Upload lab reports", accept_multiple_files=True, 
                                            type=['pdf', 'jpg', 'jpeg', 'png'])
            
            submitted = st.form_submit_button("Submit Consultation Request")
            
            if submitted and doctor_id:
                consultation_data = Consultation(
                    patient_id=user_id,
                    doctor_id=doctor_id,
                    symptoms=symptoms,
                    medical_history=medical_history.split(',') if medical_history else [],
                    allergies=allergies.split(',') if allergies else [],
                    status="pending"
                )
                
                result = consultations_collection.insert_one(consultation_data.to_dict())
                
                if result.inserted_id:
                    st.success("Consultation request submitted successfully!")
                else:
                    st.error("Failed to submit consultation request")
    
    elif choice == "Re-consultation":
        st.header("🔄 Re-consultation")
        
        # Get patient's previous consultations
        previous_consultations = list(consultations_collection.find(
            {"patient_id": user_id}
        ).sort("created_at", -1))
        
        if not previous_consultations:
            st.info("No previous consultations found. Please start with a new consultation.")
            return
        
        consultation_options = {}
        for consult in previous_consultations:
            doctor = get_user_by_id(consult["doctor_id"])
            doctor_name = doctor["name"] if doctor else "Unknown Doctor"
            label = f"Consultation with Dr. {doctor_name} - {consult['created_at'].strftime('%Y-%m-%d')}"
            consultation_options[label] = consult["_id"]
        
        selected_consultation_label = st.selectbox("Select Previous Consultation", list(consultation_options.keys()))
        consultation_id = consultation_options[selected_consultation_label]
        
        selected_consultation = consultations_collection.find_one({"_id": consultation_id})
        
        if selected_consultation:
            st.subheader("Previous Consultation Details")
            st.write(f"**Symptoms:** {selected_consultation['symptoms']}")
            st.write(f"**Diagnosis:** {selected_consultation.get('diagnosis', 'Not provided')}")
            st.write(f"**Status:** {selected_consultation['status']}")
            
            with st.form("re_consultation"):
                st.subheader("New Information")
                new_symptoms = st.text_area("New Symptoms or Updates")
                
                st.subheader("Upload New Lab Reports")
                new_uploads = st.file_uploader("Upload new lab reports", accept_multiple_files=True,
                                             type=['pdf', 'jpg', 'jpeg', 'png'])
                
                submitted = st.form_submit_button("Submit Re-consultation")
                
                if submitted:
                    # Create new consultation referencing the previous one
                    new_consultation = Consultation(
                        patient_id=user_id,
                        doctor_id=selected_consultation["doctor_id"],
                        symptoms=f"Follow-up: {selected_consultation['symptoms']}\nNew: {new_symptoms}",
                        medical_history=selected_consultation.get("medical_history", []),
                        allergies=selected_consultation.get("allergies", []),
                        status="pending"
                    )
                    
                    result = consultations_collection.insert_one(new_consultation.to_dict())
                    
                    if result.inserted_id:
                        st.success("Re-consultation request submitted successfully!")
                    else:
                        st.error("Failed to submit re-consultation request")
    
    elif choice == "Consultation History":
        st.header("📋 Consultation History")
        
        consultations = list(consultations_collection.find(
            {"patient_id": user_id}
        ).sort("created_at", -1))
        
        if not consultations:
            st.info("No consultation history found.")
            return
        
        for consult in consultations:
            doctor = get_user_by_id(consult["doctor_id"])
            doctor_name = doctor["name"] if doctor else "Unknown Doctor"
            specialization = doctor["specialization"] if doctor else "N/A"
            
            with st.expander(f"Consultation with Dr. {doctor_name} ({specialization}) - {consult['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Status:** {consult['status']}")
                    st.write(f"**Symptoms:** {consult['symptoms']}")
                    st.write(f"**Allergies:** {', '.join(consult.get('allergies', []))}")
                
                with col2:
                    st.write(f"**Diagnosis:** {consult.get('diagnosis', 'Not provided')}")
                    st.write(f"**Prescription:** {consult.get('prescription', 'Not provided')}")
                    st.write(f"**Consultation Notes:** {consult.get('consultation_notes', 'Not provided')}")
                
                if consult.get('lab_requests'):
                    st.write("**Lab Requests:**")
                    for lab_req in consult['lab_requests']:
                        st.write(f"- {lab_req}")