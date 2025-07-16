import streamlit as st
from payment_plans import PaymentPlans, UsageTracker
from login_ui import check_authentication

# Configure page
st.set_page_config(
    page_title="Pricing - Emoticon",
    page_icon="💰",
    layout="wide"
)

# Initialize authentication
check_authentication()

st.title("💰 Pricing Plans")
st.markdown("*Choose the plan that works best for your emotion analysis needs*")

# Get current user plan and usage
current_plan = PaymentPlans.get_user_plan()
usage_stats = UsageTracker.get_usage_stats()

# Pricing Plans
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # Free Plan
    st.markdown("### 🆓 Free Plan")
    st.markdown("**$0/month**")
    
    st.markdown("**Perfect for trying out emotion analysis**")
    st.markdown("• 5 analyses per day")
    st.markdown("• 1 lie detection per day")
    st.markdown("• 1 stress analysis per day")
    st.markdown("• Basic emotion analysis")
    st.markdown("• Image and video upload")
    st.markdown("• Live camera analysis")
    
    if current_plan == 'free':
        st.success("✅ Current Plan")
    else:
        if st.button("Select Free Plan", key="select_free", use_container_width=True):
            st.info("Contact support to change your plan")

with col2:
    # Professional Plan
    st.markdown("### ⭐ Professional Plan")
    st.markdown("**$14.99/month**")
    
    st.markdown("**For serious emotion analysis and professional use**")
    st.markdown("• **Unlimited** daily analyses")
    st.markdown("• **Unlimited** lie detection")
    st.markdown("• **Unlimited** stress analysis")
    st.markdown("• Advanced AI insights")
    st.markdown("• Priority support")
    st.markdown("• Export analysis results")
    st.markdown("• Analysis history")
    
    if current_plan == 'professional':
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Professional", key="upgrade_professional", type="primary", use_container_width=True):
            st.info("🚧 Stripe integration coming soon! Contact support for manual upgrade.")

# Usage Comparison
st.markdown("---")
st.markdown("## 📊 Usage Comparison")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Daily Analyses")
    st.markdown("**Free:** 5 per day")
    st.markdown("**Professional:** Unlimited")
    
    if usage_stats['today'] > 0:
        st.markdown(f"**Your usage today:** {usage_stats['today']}")

with col2:
    st.markdown("### Lie Detection")
    st.markdown("**Free:** 1 per day")
    st.markdown("**Professional:** Unlimited")

with col3:
    st.markdown("### Stress Analysis")
    st.markdown("**Free:** 1 per day")
    st.markdown("**Professional:** Unlimited")

# Features Comparison
st.markdown("---")
st.markdown("## 🔧 Features Comparison")

features = [
    ("Basic Emotion Analysis", "✅", "✅"),
    ("Image Upload", "✅", "✅"),
    ("Video Upload", "✅", "✅"),
    ("Live Camera", "✅", "✅"),
    ("Screen Recording", "✅", "✅"),
    ("Lie Detection", "1/day", "Unlimited"),
    ("Stress Analysis", "1/day", "Unlimited"),
    ("Daily Analyses", "5/day", "Unlimited"),
    ("Analysis History", "❌", "✅"),
    ("Export Results", "❌", "✅"),
    ("Priority Support", "❌", "✅"),
    ("Advanced AI Insights", "❌", "✅"),
]

# Create feature comparison table
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.markdown("**Feature**")
with col2:
    st.markdown("**Free**")
with col3:
    st.markdown("**Professional**")

for feature, free_val, pro_val in features:
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(feature)
    with col2:
        st.markdown(free_val)
    with col3:
        st.markdown(pro_val)

# FAQ Section
st.markdown("---")
st.markdown("## ❓ Frequently Asked Questions")

with st.expander("How does the free plan work?"):
    st.markdown("""
    The free plan gives you 5 emotion analyses per day, plus 1 lie detection and 1 stress analysis. 
    This is perfect for trying out our system and getting familiar with the features.
    """)

with st.expander("What happens if I exceed my daily limit?"):
    st.markdown("""
    If you exceed your daily limit, you'll need to wait until the next day for your quota to reset, 
    or you can upgrade to the Professional plan for unlimited usage.
    """)

with st.expander("Can I upgrade or downgrade anytime?"):
    st.markdown("""
    Yes! You can upgrade to Professional anytime. For downgrades, please contact our support team.
    """)

with st.expander("Is there a free trial for Professional?"):
    st.markdown("""
    Currently, we offer a generous free plan that lets you test all features. 
    We may introduce free trials in the future.
    """)

with st.expander("How accurate is the emotion detection?"):
    st.markdown("""
    Our AI uses advanced computer vision and is powered by OpenAI's latest models. 
    Accuracy depends on lighting conditions, camera quality, and facial visibility.
    """)

# Support Section
st.markdown("---")
st.markdown("## 💬 Need Help?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Have questions about pricing?**")
    st.markdown("Contact our support team:")
    st.markdown("📧 support@emoticon.ai")

with col2:
    st.markdown("**Want to see a demo?**")
    if st.button("Try Free Analysis", key="try_free", type="primary"):
        st.switch_page("app.py")

# Back to App
st.markdown("---")
if st.button("← Back to App", key="back_to_app"):
    st.switch_page("app.py")