#!/usr/bin/env python3
"""
Admin script to upgrade user access
"""
import streamlit as st

def upgrade_user_to_pro(email: str):
    """Upgrade user to professional plan"""
    # Check if user exists and is logged in
    if st.session_state.get('user_email') == email:
        st.session_state.user_plan = 'pro'
        st.session_state.daily_usage = 0  # Reset usage
        return True
    return False

# Run upgrade for garryyuan1@gmail.com
if __name__ == "__main__":
    print("Upgrading user access...")
    # This would normally be run as a separate admin script
    # For now, we'll add it to the app