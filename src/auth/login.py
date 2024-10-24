import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def login_page():
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")