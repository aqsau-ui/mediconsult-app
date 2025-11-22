# pages/doctor_dashboard.py
import streamlit as st
from datetime import datetime
from database.connection import db
from config import CONSULTATIONS_COLLECTION
from utils import get_user_by_id

def doctor_dashboard():
    st.title("👨‍⚕️ Doctor Dashboard")
    
    user_id = st.session_state.user_id
    user_type = st.session_state.user_type
    
    if user_type != "doctor":
        st.error("Access denied. Doctors only.")
        return
    
    # Sidebar navigation
    menu = ["New Consultations", "Patient History", "My Consultations"]
    choice = st.sidebar.selectbox("Navigation", menu)
    
    consultations_collection = db.get_collection(CONSULTATIONS_COLLECTION)
    
    if choice == "New Consultations":
        st.header("🆕 New Consultation Requests")
        
        # Get pending consultations for this doctor
        pending_consultations = list(consultations_collection.find({
            "doctor_id": user_id,
            "status": "pending"
        }).sort("created_at", -1))
        
        if not pending_consultations:
            st.info("No new consultation requests.")
            return
        
        for consult in pending_consultations:
            patient = get_user_by_id(consult["patient_id"])
            patient_name = patient["name"] if patient else "Unknown Patient"
            
            with st.expander(f"Consultation Request from {patient_name} - {consult['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                st.subheader("Patient Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {patient_name}")
                    st.write(f"**Age:** {patient.get('age', 'Not provided')}")
                    st.write(f"**Gender:** {patient.get('gender', 'Not provided')}")
                
                with col2:
                    st.write(f"**Allergies:** {', '.join(consult.get('allergies', []))}")
                    st.write(f"**Medical History:** {', '.join(consult.get('medical_history', []))}")
                
                st.subheader("Current Symptoms")
                st.write(consult["symptoms"])
                
                # Doctor's response form
                with st.form(key=f"response_form_{consult['_id']}"):
                    diagnosis = st.text_area("Diagnosis")
                    prescription = st.text_area("Prescription")
                    lab_requests = st.text_area("Lab Requests (one per line)")
                    consultation_notes = st.text_area("Consultation Notes")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status = st.selectbox("Status", ["in_progress", "completed"], key=f"status_{consult['_id']}")
                    
                    with col2:
                        st.write("")  # Spacer
                        submitted = st.form_submit_button("Update Consultation")
                    
                    if submitted:
                        update_data = {
                            "diagnosis": diagnosis,
                            "prescription": prescription,
                            "consultation_notes": consultation_notes,
                            "status": status,
                            "updated_at": datetime.utcnow()
                        }
                        
                        if lab_requests:
                            update_data["lab_requests"] = [req.strip() for req in lab_requests.split('\n') if req.strip()]
                        
                        result = consultations_collection.update_one(
                            {"_id": consult["_id"]},
                            {"$set": update_data}
                        )
                        
                        if result.modified_count > 0:
                            st.success("Consultation updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update consultation")
    
    elif choice == "Patient History":
        st.header("📋 Patient History")
        
        # Get all patients who consulted this doctor
        patient_consultations = list(consultations_collection.find({
            "doctor_id": user_id
        }).sort("created_at", -1))
        
        if not patient_consultations:
            st.info("No patient history found.")
            return
        
        # Group by patient
        patients_data = {}
        for consult in patient_consultations:
            patient_id = consult["patient_id"]
            if patient_id not in patients_data:
                patient = get_user_by_id(patient_id)
                patients_data[patient_id] = {
                    "patient_info": patient,
                    "consultations": []
                }
            patients_data[patient_id]["consultations"].append(consult)
        
        for patient_id, data in patients_data.items():
            patient = data["patient_info"]
            consultations = data["consultations"]
            
            with st.expander(f"Patient: {patient['name']} (Age: {patient.get('age', 'N/A')}, Gender: {patient.get('gender', 'N/A')})"):
                for consult in consultations:
                    st.write(f"**Date:** {consult['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Symptoms:** {consult['symptoms']}")
                    st.write(f"**Diagnosis:** {consult.get('diagnosis', 'Not provided')}")
                    st.write(f"**Status:** {consult['status']}")
                    st.write("---")
    
    elif choice == "My Consultations":
        st.header("📊 My Consultations Overview")
        
        all_consultations = list(consultations_collection.find({
            "doctor_id": user_id
        }).sort("created_at", -1))
        
        if not all_consultations:
            st.info("No consultations found.")
            return
        
        # Statistics
        total_consultations = len(all_consultations)
        pending_count = len([c for c in all_consultations if c["status"] == "pending"])
        completed_count = len([c for c in all_consultations if c["status"] == "completed"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Consultations", total_consultations)
        col2.metric("Pending", pending_count)
        col3.metric("Completed", completed_count)
        
        # Display all consultations
        st.subheader("All Consultations")
        for consult in all_consultations:
            patient = get_user_by_id(consult["patient_id"])
            patient_name = patient["name"] if patient else "Unknown Patient"
            
            status_color = {
                "pending": "🟡",
                "in_progress": "🔵", 
                "completed": "🟢"
            }.get(consult["status"], "⚪")
            
            st.write(f"{status_color} **{patient_name}** - {consult['created_at'].strftime('%Y-%m-%d')} - Status: {consult['status']}")