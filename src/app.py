import streamlit as st
from auth.login import login_page
from database.airtable_manager import AirtableManager
import pages.principal as principal
import pages.dashboard as dashboard


def clear_session():
    # Limpa todas as credenciais e tokens
    st.session_state.authenticated = False
    if 'saved_credentials' in st.session_state:
        del st.session_state.saved_credentials
    if 'refresh_token' in st.session_state:
        del st.session_state.refresh_token
    # Limpa qualquer outro estado da sessão se necessário
    for key in list(st.session_state.keys()):
        if key.startswith('form_'):
            del st.session_state[key]


def main():
    st.set_page_config(page_title="Records Management System", layout="wide",initial_sidebar_state="collapsed")
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
    else:
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a page", 
            ["Records", "Dashboard"]
        )
        
        if page == "Records":
            principal.show()
        elif page == "Dashboard":
            dashboard.show()

        
        if st.sidebar.button("Logout"):
            clear_session()
            st.rerun()

if __name__ == "__main__":
    main()