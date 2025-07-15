import streamlit as st
from auth import auth_system
from datetime import datetime
import time

def show_login_form():
    """Display login form"""
    st.markdown("### Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_login = st.form_submit_button("Login", use_container_width=True)
        with col2:
            if st.form_submit_button("Switch to Register", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
    
    if submit_login:
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            with st.spinner("Logging in..."):
                result = auth_system.login_user(email, password)
                
                if result['success']:
                    st.session_state.logged_in = True
                    st.session_state.user_email = result['email']
                    st.session_state.user_id = result['user_id']
                    st.session_state.session_token = result['session_token']
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result['error'])

def show_register_form():
    """Display registration form"""
    st.markdown("### Create New Account")
    
    with st.form("register_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Password requirements
        st.markdown("""
        **Password Requirements:**
        - At least 8 characters long
        - Contains uppercase and lowercase letters
        - Contains at least one number
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            submit_register = st.form_submit_button("Register", use_container_width=True)
        with col2:
            if st.form_submit_button("Switch to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
    
    if submit_register:
        if not email or not password or not confirm_password:
            st.error("Please fill in all fields")
        elif password != confirm_password:
            st.error("Passwords do not match")
        else:
            with st.spinner("Creating account..."):
                result = auth_system.register_user(email, password)
                
                if result['success']:
                    st.success("Account created successfully! Please login.")
                    st.session_state.show_register = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result['error'])
                    if 'details' in result:
                        for detail in result['details']:
                            st.error(f"• {detail}")

def show_user_menu():
    """Display user menu for logged in users"""
    if st.session_state.get('logged_in', False):
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**Logged in as:** {st.session_state.get('user_email', 'User')}")
            
            if st.button("Account Settings", use_container_width=True):
                st.session_state.show_account_settings = True
            
            if st.button("Logout", use_container_width=True):
                logout_user()

def logout_user():
    """Logout current user"""
    if st.session_state.get('session_token'):
        auth_system.logout_user(st.session_state.session_token)
    
    # Clear session state
    keys_to_clear = ['logged_in', 'user_email', 'user_id', 'session_token', 'show_account_settings']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Logged out successfully")
    time.sleep(1)
    st.rerun()

def show_account_settings():
    """Display account settings modal"""
    st.markdown("### Account Settings")
    
    # Get user info
    user_info = auth_system.get_user_info(st.session_state.user_id)
    
    if user_info['success']:
        user_data = user_info['user']
        
        st.markdown(f"**Email:** {user_data['email']}")
        st.markdown(f"**Account Created:** {datetime.fromisoformat(user_data['created_at']).strftime('%B %d, %Y')}")
        if user_data['last_login']:
            st.markdown(f"**Last Login:** {datetime.fromisoformat(user_data['last_login']).strftime('%B %d, %Y at %I:%M %p')}")
        
        st.markdown("---")
        
        # Change password section
        st.markdown("#### Change Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_change = st.form_submit_button("Change Password", use_container_width=True)
            with col2:
                if st.form_submit_button("Close", use_container_width=True):
                    st.session_state.show_account_settings = False
                    st.rerun()
        
        if submit_change:
            if not current_password or not new_password or not confirm_new_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match")
            else:
                with st.spinner("Changing password..."):
                    result = auth_system.change_password(
                        st.session_state.user_id,
                        current_password,
                        new_password
                    )
                    
                    if result['success']:
                        st.success("Password changed successfully!")
                        time.sleep(1)
                        st.session_state.show_account_settings = False
                        st.rerun()
                    else:
                        st.error(result['error'])
                        if 'details' in result:
                            for detail in result['details']:
                                st.error(f"• {detail}")
    else:
        st.error("Unable to load account information")

def check_authentication():
    """Check if user is authenticated and session is valid"""
    if st.session_state.get('logged_in', False) and st.session_state.get('session_token'):
        # Validate session
        result = auth_system.validate_session(st.session_state.session_token)
        
        if not result['valid']:
            # Session expired or invalid
            logout_user()
            return False
        
        return True
    
    return False

def require_authentication():
    """Require user to be authenticated to access content"""
    if not check_authentication():
        st.markdown("## Welcome to Emoticon")
        st.markdown("*Please login or register to access the emotion analysis platform*")
        
        # Initialize registration state
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        
        # Show appropriate form
        if st.session_state.show_register:
            show_register_form()
        else:
            show_login_form()
        
        return False
    
    return True

def init_auth_session():
    """Initialize authentication session state"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    
    if 'show_account_settings' not in st.session_state:
        st.session_state.show_account_settings = False