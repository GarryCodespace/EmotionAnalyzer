"""
Pricing Page for Emoticon App
Displays subscription plans and handles upgrades
"""

import streamlit as st
from payment_ui import PaymentUI, show_payment_success, show_payment_canceled
from payment_plans import PaymentPlans, UsageTracker
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login_ui import check_authentication

def show_pricing_page():
    """Main pricing page"""
    st.set_page_config(page_title="Emoticon - Pricing", layout="wide")
    
    # Check for payment success/cancel
    if 'success' in st.query_params:
        show_payment_success()
        return
    elif 'canceled' in st.query_params:
        show_payment_canceled()
        return
    
    # Initialize authentication
    check_authentication()
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>Pricing Plans</h1>
        <p style="font-size: 1.2rem; color: #666;">Choose the perfect plan for your emotion analysis needs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize payment UI
    payment_ui = PaymentUI()
    
    # Show pricing plans
    payment_ui.show_pricing_page()
    
    # Add feature comparison table
    st.markdown("---")
    st.markdown("### Feature Comparison")
    
    # Create comparison table
    features = [
        "Daily Analyses",
        "Save History",
        "Lie Detector",
        "Body Language Analysis",
        "API Access",
        "Priority Support",
        "Export Data",
        "Custom Models"
    ]
    
    plans = ['free', 'basic', 'pro', 'enterprise']
    plan_names = [PaymentPlans.get_plan_info(p)['name'] for p in plans]
    
    # Create table data
    table_data = []
    for feature in features:
        row = [feature]
        for plan in plans:
            limits = PaymentPlans.get_usage_limits(plan)
            if feature == "Daily Analyses":
                if limits['daily_analyses'] == -1:
                    row.append("Unlimited")
                else:
                    row.append(str(limits['daily_analyses']))
            elif feature == "Save History":
                row.append("✅" if limits['save_history'] else "❌")
            elif feature == "Lie Detector":
                row.append("✅" if limits['lie_detector'] else "❌")
            elif feature == "Body Language Analysis":
                row.append("✅" if limits['advanced_features'] else "❌")
            elif feature == "API Access":
                row.append("✅" if limits['api_access'] else "❌")
            elif feature == "Priority Support":
                row.append("✅" if plan in ['pro', 'enterprise'] else "❌")
            elif feature == "Export Data":
                row.append("✅" if plan in ['basic', 'pro', 'enterprise'] else "❌")
            elif feature == "Custom Models":
                row.append("✅" if plan == 'enterprise' else "❌")
            else:
                row.append("❌")
        table_data.append(row)
    
    # Display table
    col_widths = [2, 1, 1, 1, 1]
    cols = st.columns(col_widths)
    
    # Header row
    cols[0].markdown("**Feature**")
    for i, name in enumerate(plan_names):
        cols[i+1].markdown(f"**{name}**")
    
    # Data rows
    for row in table_data:
        cols = st.columns(col_widths)
        for i, cell in enumerate(row):
            cols[i].markdown(cell)
    
    # FAQ Section
    st.markdown("---")
    st.markdown("### ❓ Frequently Asked Questions")
    
    with st.expander("Can I change my plan anytime?"):
        st.markdown("Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.")
    
    with st.expander("What happens to my data if I cancel?"):
        st.markdown("Your analysis history is preserved for 30 days after cancellation. You can reactivate to restore access.")
    
    with st.expander("Do you offer refunds?"):
        st.markdown("We offer a 7-day money-back guarantee for all paid plans. Contact support for assistance.")
    
    with st.expander("Is there a free trial?"):
        st.markdown("Yes! The Free plan gives you 5 analyses per day to try our features before upgrading.")
    
    with st.expander("How accurate is the emotion detection?"):
        st.markdown("Our AI achieves 94% accuracy using advanced computer vision and GPT-4o analysis.")
    
    # Contact information
    st.markdown("---")
    st.markdown("### 📞 Need Help?")
    st.markdown("Contact our support team at **emoticon.contact@gmail.com** or call **+61 451 961 015**")

if __name__ == "__main__":
    show_pricing_page()