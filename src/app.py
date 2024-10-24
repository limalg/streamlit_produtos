import streamlit as st
from auth.login import login_page
from database.airtable_manager import AirtableManager
import pages.principal as principal
import pages.dashboard as dashboard


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
            st.session_state.authenticated = False
            st.rerun()

if __name__ == "__main__":
    main()
