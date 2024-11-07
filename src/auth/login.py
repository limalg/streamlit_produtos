import streamlit as st
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
import jwt
from datetime import datetime, timedelta
import json

@dataclass
class Credentials:
    username: str
    password: str
    remember_me: bool = False

class AuthManager:
    def __init__(self):
        load_dotenv()
        self.admin_credentials = Credentials(
            username=os.getenv("ADMIN_USERNAME", ""),
            password=os.getenv("ADMIN_PASSWORD", "")
        )
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        
    def validate_credentials(self, credentials: Credentials) -> bool:
        return (credentials.username == self.admin_credentials.username and 
                credentials.password == self.admin_credentials.password)
    
    def create_refresh_token(self, username: str) -> str:
        expiration = datetime.utcnow() + timedelta(days=30)
        return jwt.encode(
            {"username": username, "exp": expiration},
            self.secret_key,
            algorithm="HS256"
        )
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("username")
        except:
            return None

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False
    if 'saved_username' not in st.session_state:
        st.session_state.saved_username = ""

class LoginUI:
    @staticmethod
    def render() -> Optional[Credentials]:
        st.title("Login")
        
        saved_username = st.session_state.get('saved_username', '')
        
        username = st.text_input("Username", value=saved_username)
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me", value=st.session_state.get('remember_me', False))
        
        if st.button("Login"):
            return Credentials(
                username=username,
                password=password,
                remember_me=remember_me
            )
        return None

def login_page():
    init_session_state()
    auth_manager = AuthManager()
    
    # Verificar token de refresh
    if not st.session_state.authenticated and 'refresh_token' in st.session_state:
        token = st.session_state.refresh_token
        username = auth_manager.validate_refresh_token(token)
        if username:
            st.session_state.authenticated = True
            st.session_state.saved_username = username
            st.rerun()
    
    credentials = LoginUI.render()
    
    if credentials:
        if auth_manager.validate_credentials(credentials):
            st.session_state.authenticated = True
            
            if credentials.remember_me:
                # Salvar credenciais e token de refresh
                st.session_state.remember_me = True
                st.session_state.saved_username = credentials.username
                st.session_state.refresh_token = auth_manager.create_refresh_token(
                    credentials.username
                )
            else:
                # Limpar dados salvos se "remember me" não estiver marcado
                st.session_state.remember_me = False
                st.session_state.saved_username = ""
                if 'refresh_token' in st.session_state:
                    del st.session_state.refresh_token
            
            st.rerun()
        else:
            st.error("Invalid credentials")