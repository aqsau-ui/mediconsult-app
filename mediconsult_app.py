# mediconsult_app.py
import streamlit as st
import bcrypt
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# =============================================
# DATABASE CONNECTION (No imports needed)
# =============================================

# MongoDB Configuration
client = MongoClient("mongodb://mongodb:27017/") 
db = client["mediconsult"]

# Collections
USERS_COLLECTION = "users"
CONSULTATIONS_COLLECTION = "consultations"

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

# =============================================
# UTILITY FUNCTIONS
# =============================================

def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(password, hashed):
    pwd_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def register_user(name, email, password, user_type, **kwargs):
    users_collection = db[USERS_COLLECTION]
    
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
        **kwargs,
        "created_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_data)
    return True, "User registered successfully"

def authenticate_user(email, password):
    users_collection = db[USERS_COLLECTION]
    user = users_collection.find_one({"email": email})
    
    if user and verify_password(password, user["password"]):
        return True, user
    return False, None

def get_user_by_id(user_id):
    users_collection = db[USERS_COLLECTION]
    return users_collection.find_one({"_id": user_id})

def get_doctors_by_specialization(specialization=None):
    users_collection = db[USERS_COLLECTION]
    query = {"user_type": "doctor"}
    if specialization:
        query["specialization"] = specialization
    return list(users_collection.find(query))

def get_all_doctors():
    users_collection = db[USERS_COLLECTION]
    return list(users_collection.find({"user_type": "doctor"}))

def setup_database():
    """Initialize database with admin and sample doctors"""
    users_collection = db[USERS_COLLECTION]
    
    # Create admin user if not exists
    admin_user = users_collection.find_one({"email": "admin@mediconsult.com"})
    if not admin_user:
        admin_data = {
            "name": "System Administrator",
            "email": "admin@mediconsult.com",
            "password": hash_password("admin123"),
            "user_type": "admin",
            "phone": "+1234567890",
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(admin_data)
        st.sidebar.success("✅ Admin: admin@mediconsult.com / admin123")
    
    # Create sample doctors
    sample_doctors = [
        {
            "name": "Sarah Wilson",
            "email": "cardio@mediconsult.com",
            "password": hash_password("doctor123"),
            "user_type": "doctor",
            "specialization": "Cardiologist",
            "qualifications": "MD Cardiology, 10 years experience",
            "consultation_fee": 100,
            "available_hours": "Mon-Fri 9AM-5PM",
            "phone": "+1234567891",
            "is_available": True,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Michael Chen",
            "email": "derma@mediconsult.com",
            "password": hash_password("doctor123"),
            "user_type": "doctor",
            "specialization": "Dermatologist",
            "qualifications": "MD Dermatology, Skin specialist",
            "consultation_fee": 80,
            "available_hours": "Mon-Wed-Fri 10AM-6PM",
            "phone": "+1234567892",
            "is_available": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    for doctor in sample_doctors:
        if not users_collection.find_one({"email": doctor["email"]}):
            users_collection.insert_one(doctor)
    
    # Create indexes
    users_collection.create_index("email", unique=True)
    users_collection.create_index("user_type")
    users_collection.create_index("specialization")

# =============================================
# STREAMLIT APP CONFIGURATION
# =============================================

# Hide Streamlit menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="MediConsult - Patient-Doctor Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# DASHBOARD FUNCTIONS
# =============================================

def patient_dashboard():
    st.title("👨‍💼 Patient Dashboard")
    
    user_id = st.session_state.user_id
    consultations_collection = db[CONSULTATIONS_COLLECTION]
    
    # Sidebar navigation
    menu = ["Find Doctors", "New Consultation", "Consultation History"]
    choice = st.sidebar.selectbox("Navigation", menu)
    
    if choice == "Find Doctors":
        st.header("👨‍⚕️ Find Available Doctors")
        
        doctors = get_all_doctors()
        
        if not doctors:
            st.info("No doctors found.")
            return
        
        for doctor in doctors:
            with st.container():
                st.subheader(f"Dr. {doctor['name']}")
                st.write(f"**Specialization:** {doctor.get('specialization', 'Not specified')}")
                st.write(f"**Qualifications:** {doctor.get('qualifications', 'Not provided')}")
                st.write(f"**Fee:** ${doctor.get('consultation_fee', 'N/A')}")
                
                if st.button(f"Book Consultation", key=f"book_{doctor['_id']}"):
                    st.session_state.selected_doctor = doctor
                    st.rerun()
        
        if st.session_state.get('selected_doctor'):
            doctor = st.session_state.selected_doctor
            st.markdown("""
                <style>
                .consultation-header {
                    color: #0d47a1;
                    font-size: 1.8rem;
                    font-weight: bold;
                    margin-bottom: 1.5rem;
                    padding: 10px;
                    background-color: #e3f2fd;
                    border-radius: 8px;
                    text-align: center;
                }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="consultation-header">📅 Book Consultation with Dr. {doctor["name"]}</div>', unsafe_allow_html=True)
            
            with st.form("quick_consultation"):
                st.write(f"**Doctor:** Dr. {doctor['name']} ({doctor.get('specialization', 'General Physician')})")
                st.write(f"**Fee:** ${doctor.get('consultation_fee', 'N/A')}")
                
                symptoms = st.text_area("Describe Your Symptoms", placeholder="Please describe your symptoms in detail...", height=100)
                medical_history = st.text_area("Medical History (Optional)")
                allergies = st.text_area("Allergies (Optional)")
                
                submitted = st.form_submit_button("Submit Consultation Request")
                
                if submitted:
                    if not symptoms:
                        st.error("Please describe your symptoms")
                    else:
                        consultation_data = {
                            "patient_id": user_id,
                            "doctor_id": doctor["_id"],
                            "doctor_name": doctor["name"],
                            "doctor_specialization": doctor.get("specialization"),
                            "symptoms": symptoms,
                            "medical_history": medical_history.split(',') if medical_history else [],
                            "allergies": allergies.split(',') if allergies else [],
                            "consultation_fee": doctor.get("consultation_fee"),
                            "status": "pending",
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        
                        result = consultations_collection.insert_one(consultation_data)
                        
                        if result.inserted_id:
                            st.success("✅ Consultation request submitted successfully!")
                            st.session_state.selected_doctor = None
                            st.rerun()
    
    elif choice == "New Consultation":
        st.header("🆕 New Consultation")
        
        doctors = get_all_doctors()
        if not doctors:
            st.info("No doctors available.")
            return
        
        doctor_options = {f"Dr. {doc['name']} ({doc.get('specialization')})": doc["_id"] for doc in doctors}
        selected_doctor_label = st.selectbox("Choose a Doctor", list(doctor_options.keys()))
        selected_doctor_id = doctor_options[selected_doctor_label]
        selected_doctor = get_user_by_id(selected_doctor_id)
        
        with st.form("consultation_form"):
            symptoms = st.text_area("Symptoms", placeholder="Describe your symptoms...")
            submitted = st.form_submit_button("Submit Consultation")
            
            if submitted and symptoms:
                consultation_data = {
                    "patient_id": user_id,
                    "doctor_id": selected_doctor_id,
                    "doctor_name": selected_doctor['name'],
                    "symptoms": symptoms,
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                consultations_collection.insert_one(consultation_data)
                st.success("Consultation request submitted!")
    
    elif choice == "Consultation History":
        st.header("📋 Consultation History")
        
        consultations = list(consultations_collection.find({"patient_id": user_id}).sort("created_at", -1))
        
        for consult in consultations:
            with st.expander(f"Consultation with Dr. {consult.get('doctor_name', 'Unknown')} - {consult['created_at'].strftime('%Y-%m-%d')}"):
                st.write(f"**Symptoms:** {consult['symptoms']}")
                st.write(f"**Status:** {consult['status']}")
                st.write(f"**Diagnosis:** {consult.get('diagnosis', 'Not provided yet')}")

def doctor_dashboard():
    st.title("👨‍⚕️ Doctor Dashboard")
    
    user_id = st.session_state.user_id
    consultations_collection = db[CONSULTATIONS_COLLECTION]
    
    # Get pending consultations
    pending_consultations = list(consultations_collection.find({
        "doctor_id": user_id,
        "status": "pending"
    }))
    
    st.header(f"🆕 Pending Consultations ({len(pending_consultations)})")
    
    for consult in pending_consultations:
        patient = get_user_by_id(consult["patient_id"])
        with st.expander(f"Consultation from {patient['name']}"):
            st.write(f"**Symptoms:** {consult['symptoms']}")
            
            with st.form(key=f"response_{consult['_id']}"):
                diagnosis = st.text_area("Diagnosis")
                prescription = st.text_area("Prescription")
                
                if st.form_submit_button("Complete Consultation"):
                    consultations_collection.update_one(
                        {"_id": consult["_id"]},
                        {"$set": {
                            "diagnosis": diagnosis,
                            "prescription": prescription,
                            "status": "completed",
                            "updated_at": datetime.utcnow()
                        }}
                    )
                    st.success("Consultation completed!")
                    st.rerun()

def admin_dashboard():
    st.title("🔧 Admin Dashboard")
    
    users_collection = db[USERS_COLLECTION]
    consultations_collection = db[CONSULTATIONS_COLLECTION]
    
    # Statistics
    total_users = users_collection.count_documents({})
    total_patients = users_collection.count_documents({"user_type": "patient"})
    total_doctors = users_collection.count_documents({"user_type": "doctor"})
    total_consultations = consultations_collection.count_documents({})
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", total_users)
    col2.metric("Patients", total_patients)
    col3.metric("Doctors", total_doctors)
    col4.metric("Consultations", total_consultations)
    
    st.subheader("User Management")
    users = list(users_collection.find({}, {"password": 0}))
    
    for user in users:
        st.write(f"**{user['name']}** ({user['user_type']}) - {user['email']}")

# =============================================
# MAIN APPLICATION
# =============================================

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_type = None
        st.session_state.user_name = None
    
    # Setup database (creates admin user if needed)
    setup_database()
    
    # Header
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🏥 MediConsult</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #2e86ab;">Patient-Doctor Consultation Portal</h3>', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Login/Register Interface
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                user_type = st.selectbox("Login as", ["Patient", "Doctor", "Admin"])
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    success, user = authenticate_user(email, password)
                    if success and user["user_type"].lower() == user_type.lower():
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["_id"]
                        st.session_state.user_type = user["user_type"]
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("register_form"):
                user_type = st.selectbox("Register as", ["Patient", "Doctor"])
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                phone = st.text_input("Phone Number")
                
                if user_type == "Doctor":
                    specialization = st.selectbox("Specialization", SPECIALIZATIONS)
                
                submitted = st.form_submit_button("Register")
                
                if submitted:
                    additional_fields = {"phone": phone}
                    if user_type == "Doctor":
                        additional_fields["specialization"] = specialization
                    
                    success, message = register_user(name, email, password, user_type.lower(), **additional_fields)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        # User is logged in - show dashboard
        st.sidebar.title(f"Welcome, {st.session_state.user_name}!")
        st.sidebar.write(f"Role: {st.session_state.user_type.title()}")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_type = None
            st.session_state.user_name = None
            st.rerun()
        
        # Route to appropriate dashboard
        if st.session_state.user_type == "patient":
            patient_dashboard()
        elif st.session_state.user_type == "doctor":
            doctor_dashboard()
        elif st.session_state.user_type == "admin":
            admin_dashboard()

if __name__ == "__main__":
    main()