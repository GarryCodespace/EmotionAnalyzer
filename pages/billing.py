import streamlit as st
from payment_plans import PaymentPlans, UsageTracker
from login_ui import check_authentication, require_authentication
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Billing - Emoticon",
    page_icon="💳",
    layout="wide"
)

# Initialize authentication
check_authentication()

# Require authentication for billing page
if not require_authentication():
    st.stop()

st.title("💳 Billing & Subscription")
st.markdown("*Manage your subscription and billing information*")

# Get current user plan and usage
current_plan = PaymentPlans.get_user_plan()
plan_info = PaymentPlans.get_plan_info(current_plan)
usage_stats = UsageTracker.get_usage_stats()

# Current Plan Section
st.markdown("---")
st.markdown("## Current Plan")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Plan:** {plan_info['name']}")
    st.markdown(f"**Price:** ${plan_info['price']}/month")
    
    # Show usage limits
    limits = PaymentPlans.get_usage_limits(current_plan)
    daily_limit = limits['daily_analyses']
    if daily_limit == -1:
        st.markdown(f"**Daily Analyses:** Unlimited")
    else:
        st.markdown(f"**Daily Analyses:** {daily_limit}")
    
    st.markdown(f"**Lie Detection:** {'Unlimited' if limits['lie_detection'] == -1 else limits['lie_detection']}")
    st.markdown(f"**Stress Analysis:** {'Unlimited' if limits['stress_analysis'] == -1 else limits['stress_analysis']}")

with col2:
    st.markdown("### Usage This Month")
    st.markdown(f"**Today:** {usage_stats['today']} analyses")
    st.markdown(f"**This Week:** {usage_stats['week']} analyses")
    st.markdown(f"**This Month:** {usage_stats['month']} analyses")
    
    # Show progress bar for daily usage
    if daily_limit != -1:
        progress = min(usage_stats['today'] / daily_limit, 1.0)
        st.progress(progress)
        if progress >= 1.0:
            st.error("Daily limit reached!")

# Available Plans Section
st.markdown("---")
st.markdown("## Available Plans")

# Free Plan
with st.expander("🆓 Free Plan - $0/month", expanded=current_plan=='free'):
    st.markdown("**Perfect for trying out emotion analysis**")
    st.markdown("• 5 analyses per day")
    st.markdown("• 1 lie detection per day")
    st.markdown("• 1 stress analysis per day")
    st.markdown("• Basic emotion analysis")
    st.markdown("• Image and video upload")
    
    if current_plan != 'free':
        if st.button("Downgrade to Free", key="downgrade_free"):
            st.info("Contact support to downgrade your plan")

# Professional Plan
with st.expander("⭐ Professional Plan - $14.99/month", expanded=current_plan=='professional'):
    st.markdown("**For serious emotion analysis and professional use**")
    st.markdown("• **Unlimited** daily analyses")
    st.markdown("• **Unlimited** lie detection")
    st.markdown("• **Unlimited** stress analysis")
    st.markdown("• Advanced AI insights")
    st.markdown("• Priority support")
    st.markdown("• Export analysis results")
    
    if current_plan != 'professional':
        if st.button("Upgrade to Professional", key="upgrade_professional", type="primary"):
            st.info("🚧 Stripe integration coming soon! Contact support for manual upgrade.")

# Billing History Section
st.markdown("---")
st.markdown("## Billing History")

# Mock billing history for demo
st.markdown("*No billing history available for free plan*")

if current_plan == 'professional':
    st.markdown("### Recent Transactions")
    
    # Sample transaction data
    transactions = [
        {"date": "2024-01-15", "amount": "$14.99", "status": "Paid", "description": "Professional Plan - Monthly"},
        {"date": "2023-12-15", "amount": "$14.99", "status": "Paid", "description": "Professional Plan - Monthly"},
        {"date": "2023-11-15", "amount": "$14.99", "status": "Paid", "description": "Professional Plan - Monthly"},
    ]
    
    for transaction in transactions:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**{transaction['date']}**")
        with col2:
            st.markdown(transaction['amount'])
        with col3:
            st.markdown(f"✅ {transaction['status']}")
        with col4:
            st.markdown(transaction['description'])

# Support Section
st.markdown("---")
st.markdown("## Support")

st.markdown("Need help with your subscription? Contact our support team:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Email Support**")
    st.markdown("📧 support@emoticon.ai")
    st.markdown("*Response time: 24 hours*")

with col2:
    st.markdown("**Live Chat**")
    if st.button("Start Chat", key="start_chat"):
        st.info("🚧 Live chat integration coming soon!")

# Back to App
st.markdown("---")
if st.button("← Back to App", key="back_to_app"):
    st.switch_page("app.py")