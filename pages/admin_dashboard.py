# app.py
import streamlit as st
from datetime import datetime
from database.connection import db
from utils import register_user, authenticate_user, get_user_by_id
from config import USERS_COLLECTION, USER_TYPE_PATIENT, USER_TYPE_DOCTOR, SPECIALIZATIONS

# Page configuration
st.set_page_config(
    page_title="MediConsult - Patient-Doctor Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_type = None
        st.session_state.user_name = None
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #2e86ab;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 MediConsult</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header">Patient-Doctor Consultation Portal</h3>', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        show_login_register()
    else:
        show_dashboard()

def show_login_register():
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "ℹ️ About"])
    
    with tab1:
        st.header("Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("Login as", ["Patient", "Doctor", "Admin"])
            
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if email and password:
                    success, user = authenticate_user(email, password)
                    if success and user["user_type"].lower() == user_type.lower():
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["_id"]
                        st.session_state.user_type = user["user_type"]
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email, password, or user type")
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.header("Register")
        
        with st.form("register_form"):
            user_type = st.selectbox("Register as", ["Patient", "Doctor"])
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            phone = st.text_input("Phone Number")
            
            if user_type == "Doctor":
                specialization = st.selectbox("Specialization", SPECIALIZATIONS)
            else:
                specialization = None
            
            if user_type == "Patient":
                age = st.number_input("Age", min_value=1, max_value=120)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            else:
                age = None
                gender = None
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if not all([name, email, password, confirm_password, phone]):
                    st.error("Please fill all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    additional_fields = {"phone": phone}
                    
                    if user_type == "Doctor":
                        additional_fields["specialization"] = specialization
                    elif user_type == "Patient":
                        additional_fields["age"] = age
                        additional_fields["gender"] = gender
                    
                    success, message = register_user(
                        name, email, password, user_type.lower(), **additional_fields
                    )
                    
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                    else:
                        st.error(message)
    
    with tab3:
        st.header("About MediConsult")
        st.markdown("""
        ### 🏥 Welcome to MediConsult
        
        **MediConsult** is a comprehensive patient-doctor consultation portal that enables:
        
        👨‍💼 **For Patients:**
        - Register and maintain personal & medical information
        - Request consultations with specialist doctors
        - Upload lab reports and medical documents
        - Request re-consultations for follow-ups
        - View complete consultation history
        
        👨‍⚕️ **For Doctors:**
        - Register with specialization
        - Receive and manage consultation requests
        - Access patient medical history
        - Provide diagnoses and prescriptions
        - Request lab tests and review reports
        
        ### 🔒 Security Features
        - Secure user authentication
        - Encrypted password storage
        - Role-based access control
        - Secure data management
        
        ### 🛠️ Technology Stack
        - **Frontend:** Streamlit
        - **Backend:** Python
        - **Database:** MongoDB
        - **Authentication:** bcrypt
        """)

def show_dashboard():
    # Sidebar with user info
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.user_name}!")
        st.write(f"Role: {st.session_state.user_type.title()}")
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_type = None
            st.session_state.user_name = None
            st.rerun()
    
    # Route to appropriate dashboard
    if st.session_state.user_type == "patient":
        from pages.patient_dashboard import patient_dashboard
        patient_dashboard()
    elif st.session_state.user_type == "doctor":
        from pages.doctor_dashboard import doctor_dashboard
        doctor_dashboard()
    elif st.session_state.user_type == "admin":
        from pages.admin_dashboard import admin_dashboard
        admin_dashboard()

if __name__ == "__main__":
    main()