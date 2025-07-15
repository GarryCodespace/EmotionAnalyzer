"""
Billing Dashboard for Emoticon App
Shows usage statistics, billing history, and account management
"""

import streamlit as st
from payment_ui import PaymentUI
from payment_plans import PaymentPlans, UsageTracker
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login_ui import check_authentication, require_authentication

def show_billing_dashboard():
    """Main billing dashboard page"""
    st.set_page_config(page_title="Emoticon - Billing", page_icon="💰", layout="wide")
    
    # Initialize authentication
    check_authentication()
    
    # Require login for billing dashboard
    if not require_authentication():
        return
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>💰 Billing Dashboard</h1>
        <p style="font-size: 1.2rem; color: #666;">Manage your subscription and view usage statistics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize payment UI
    payment_ui = PaymentUI()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Usage", "💳 Billing", "⚙️ Settings", "📈 Analytics"])
    
    with tab1:
        st.markdown("## 📊 Usage Dashboard")
        payment_ui.show_usage_dashboard()
        
        # Show detailed usage breakdown
        st.markdown("### 📈 Usage Breakdown")
        usage_stats = UsageTracker.get_usage_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Analyses", usage_stats['total'])
        with col2:
            st.metric("Today", usage_stats['today'])
        with col3:
            st.metric("This Week", usage_stats['this_week'])
        with col4:
            st.metric("This Month", usage_stats['this_month'])
        
        # Usage chart (mock data for demo)
        st.markdown("### 📊 Usage Chart")
        import pandas as pd
        import numpy as np
        
        # Generate sample data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        usage_data = pd.DataFrame({
            'Date': dates,
            'Image Analysis': np.random.randint(0, 10, len(dates)),
            'Video Analysis': np.random.randint(0, 5, len(dates)),
            'Lie Detection': np.random.randint(0, 3, len(dates))
        })
        
        st.line_chart(usage_data.set_index('Date'))
    
    with tab2:
        st.markdown("## 💳 Billing Information")
        
        # Current plan information
        current_plan = PaymentPlans.get_user_plan()
        plan_info = PaymentPlans.get_plan_info(current_plan)
        
        st.markdown("### Current Plan")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**{plan_info['name']}** - {plan_info['price_display']}")
        with col2:
            if st.button("Change Plan", key="change_plan"):
                st.session_state.show_pricing = True
                st.switch_page("pages/pricing.py")
        
        # Billing history
        payment_ui.show_billing_history()
        
        # Payment methods
        st.markdown("### 💳 Payment Methods")
        st.info("💳 Visa ending in 4242 (Default)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Payment Method"):
                st.info("Payment method management coming soon")
        with col2:
            if st.button("Update Billing Address"):
                st.info("Billing address update coming soon")
    
    with tab3:
        st.markdown("## ⚙️ Account Settings")
        
        # Plan management
        st.markdown("### Plan Management")
        current_plan = PaymentPlans.get_user_plan()
        
        if current_plan != 'free':
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Pause Subscription", key="pause_sub"):
                    st.warning("Subscription pausing coming soon")
            with col2:
                if st.button("Cancel Subscription", key="cancel_sub"):
                    st.error("Are you sure you want to cancel? Your data will be preserved for 30 days.")
        
        # Usage preferences
        st.markdown("### Usage Preferences")
        st.checkbox("Email usage reports", value=True)
        st.checkbox("Billing reminders", value=True)
        st.checkbox("Feature updates", value=False)
        
        # Data export
        st.markdown("### Data Export")
        st.markdown("Export your analysis history and usage data")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Analysis History"):
                st.info("Analysis export coming soon")
        with col2:
            if st.button("Export Usage Data"):
                st.info("Usage export coming soon")
    
    with tab4:
        st.markdown("## 📈 Analytics")
        
        # Performance metrics
        st.markdown("### Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Analysis Time", "2.3s", "+0.2s")
        with col2:
            st.metric("Success Rate", "98.7%", "+1.2%")
        with col3:
            st.metric("Monthly Growth", "+15%", "+3%")
        
        # Feature usage
        st.markdown("### Feature Usage")
        
        feature_data = {
            'Feature': ['Image Analysis', 'Video Analysis', 'Lie Detection', 'Body Language'],
            'Usage': [45, 30, 15, 10]
        }
        
        st.bar_chart(pd.DataFrame(feature_data).set_index('Feature'))
        
        # Insights
        st.markdown("### 💡 Insights")
        
        st.info("📊 You use image analysis 50% more than average users")
        st.info("🎯 Your lie detection accuracy is 12% above average")
        st.info("📈 Consider upgrading to Pro for unlimited video analysis")
    
    # Quick actions sidebar
    with st.sidebar:
        st.markdown("### Quick Actions")
        
        if st.button("Upgrade Plan", use_container_width=True):
            st.switch_page("pages/pricing.py")
        
        if st.button("Download Invoice", use_container_width=True):
            st.info("Invoice download coming soon")
        
        if st.button("Contact Support", use_container_width=True):
            st.info("Support: emoticon.contact@gmail.com")
        
        # Usage alert
        current_plan = PaymentPlans.get_user_plan()
        if current_plan == 'free':
            usage_stats = UsageTracker.get_usage_stats()
            st.warning(f"Daily usage: {usage_stats['today']}/5")
            st.info("Upgrade for unlimited analyses")

if __name__ == "__main__":
    show_billing_dashboard()