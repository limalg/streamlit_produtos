import streamlit as st
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

@dataclass
class Credentials:
    username: str
    password: str

class AuthManager:
    def __init__(self):
        load_dotenv()
        self.admin_credentials = Credentials(
            username=os.getenv("ADMIN_USERNAME", ""),
            password=os.getenv("ADMIN_PASSWORD", "")
        )

    def validate_credentials(self, credentials: Credentials) -> bool:
        return (credentials.username == self.admin_credentials.username and 
                credentials.password == self.admin_credentials.password)

class LoginUI:
    @staticmethod
    def render() -> Optional[Credentials]:
        st.title("Login")
        
        credentials = Credentials(
            username=st.text_input("Username"),
            password=st.text_input("Password", type="password")
        )
        
        if st.button("Login"):
            return credentials
        return None

def login_page():
    auth_manager = AuthManager()
    credentials = LoginUI.render()
    
    if credentials:
        if auth_manager.validate_credentials(credentials):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")