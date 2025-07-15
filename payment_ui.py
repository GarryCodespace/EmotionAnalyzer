"""
Payment UI Components for Emoticon App
Handles payment interface, plan selection, and billing
"""

import streamlit as st
import stripe
from typing import Dict, Optional
from payment_plans import PaymentPlans, UsageTracker
from datetime import datetime
import os

class PaymentUI:
    """Payment interface and billing components"""
    
    def __init__(self):
        """Initialize Stripe with API keys"""
        self.stripe_enabled = False
        
        try:
            # Try to get Stripe keys from environment or secrets
            self.stripe_public_key = os.environ.get('STRIPE_PUBLIC_KEY')
            self.stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
            
            # Also try streamlit secrets if available
            if not self.stripe_secret_key and hasattr(st, 'secrets'):
                try:
                    self.stripe_secret_key = st.secrets.get('STRIPE_SECRET_KEY')
                    self.stripe_public_key = st.secrets.get('STRIPE_PUBLIC_KEY')
                except:
                    pass
            
            # Initialize Stripe if keys are available
            if self.stripe_secret_key and self.stripe_secret_key != 'sk_test_...':
                stripe.api_key = self.stripe_secret_key
                self.stripe_enabled = True
        except Exception as e:
            # Silently handle initialization errors
            self.stripe_enabled = False
    
    def show_pricing_page(self):
        """Display pricing plans page"""
        st.title("💳 Pricing Plans")
        st.markdown("*Choose the plan that fits your needs*")
        
        # Display current plan if user is logged in
        if st.session_state.get('logged_in', False):
            current_plan = PaymentPlans.get_user_plan()
            plan_info = PaymentPlans.get_plan_info(current_plan)
            st.info(f"Current plan: **{plan_info['name']}** - {plan_info['price_display']}")
        
        # Create pricing columns
        cols = st.columns(len(PaymentPlans.PLANS))
        
        for idx, (plan_id, plan_info) in enumerate(PaymentPlans.PLANS.items()):
            with cols[idx]:
                self._render_pricing_card(plan_id, plan_info)
    
    def _render_pricing_card(self, plan_id: str, plan_info: Dict):
        """Render individual pricing card"""
        # Card styling
        card_style = "border: 2px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 10px 0;"
        if plan_info['recommended']:
            card_style = "border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 10px 0; background-color: #f8fff8;"
        
        with st.container():
            st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)
            
            # Plan header
            if plan_info['recommended']:
                st.markdown("**⭐ RECOMMENDED**")
            
            st.markdown(f"### {plan_info['name']}")
            st.markdown(f"**{plan_info['price_display']}**")
            
            # Features list
            st.markdown("**Features:**")
            for feature in plan_info['features']:
                st.markdown(f"• {feature}")
            
            # Subscribe button
            current_plan = PaymentPlans.get_user_plan()
            if plan_id == current_plan:
                st.success("Current Plan")
            elif plan_id == 'free':
                if st.button("Use Free Plan", key=f"select_{plan_id}"):
                    self._handle_plan_selection(plan_id)
            else:
                if st.button(f"Subscribe to {plan_info['name']}", key=f"select_{plan_id}"):
                    self._handle_plan_selection(plan_id)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _handle_plan_selection(self, plan_id: str):
        """Handle plan selection and payment"""
        if plan_id == 'free':
            st.session_state.user_plan = 'free'
            st.success("Switched to Free plan!")
            st.rerun()
        else:
            # For paid plans, initiate Stripe checkout
            self._initiate_stripe_checkout(plan_id)
    
    def _initiate_stripe_checkout(self, plan_id: str):
        """Initiate Stripe checkout session"""
        if not self.stripe_enabled:
            st.warning("Payment processing is not configured. Please contact support to upgrade your plan.")
            st.info("Email: emoticon.contact@gmail.com")
            return
            
        try:
            plan_info = PaymentPlans.get_plan_info(plan_id)
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan_info['price'] * 100),  # Convert to cents
                        'product_data': {
                            'name': f"Emoticon {plan_info['name']} Plan",
                            'description': f"Monthly subscription to {plan_info['name']} plan"
                        },
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"https://emotion-analyzer-z5425329.replit.app?success=true&plan={plan_id}",
                cancel_url=f"https://emotion-analyzer-z5425329.replit.app?canceled=true",
                metadata={
                    'plan_id': plan_id,
                    'user_id': str(st.session_state.get('user_id', 'guest'))
                }
            )
            
            st.markdown(f"[Complete Payment]({session.url})")
            
        except Exception as e:
            st.error(f"Payment initialization failed: {str(e)}")
    
    def show_usage_dashboard(self):
        """Display usage dashboard for current user"""
        if not st.session_state.get('logged_in', False):
            st.info("Login to view usage dashboard")
            return
        
        st.markdown("### 📊 Usage Dashboard")
        
        # Get current plan and usage stats
        current_plan = PaymentPlans.get_user_plan()
        plan_info = PaymentPlans.get_plan_info(current_plan)
        usage_stats = UsageTracker.get_usage_stats()
        limits = PaymentPlans.get_usage_limits(current_plan)
        
        # Display plan information
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Plan", plan_info['name'])
            st.metric("Monthly Cost", plan_info['price_display'])
        
        with col2:
            daily_limit = limits['daily_analyses']
            if daily_limit == -1:
                st.metric("Daily Analyses", f"{usage_stats['today']}/Unlimited")
            else:
                st.metric("Daily Analyses", f"{usage_stats['today']}/{daily_limit}")
            
            st.metric("This Month", usage_stats['this_month'])
        
        # Usage progress bar for daily limit
        if daily_limit > 0:
            progress = min(usage_stats['today'] / daily_limit, 1.0)
            st.progress(progress, f"Daily usage: {usage_stats['today']}/{daily_limit}")
        
        # Feature access
        st.markdown("### 🔓 Feature Access")
        features = [
            ("Save History", "save_history"),
            ("Lie Detector", "lie_detector"),
            ("Advanced Features", "advanced_features"),
            ("API Access", "api_access")
        ]
        
        for feature_name, feature_key in features:
            has_access = PaymentPlans.can_access_feature(feature_key, current_plan)
            status = "✅ Available" if has_access else "❌ Upgrade Required"
            st.markdown(f"**{feature_name}**: {status}")
        
        # Upgrade suggestion
        upgrade_plan = PaymentPlans.get_upgrade_suggestion(current_plan)
        if upgrade_plan:
            upgrade_info = PaymentPlans.get_plan_info(upgrade_plan)
            st.info(f"💡 Upgrade to **{upgrade_info['name']}** for {upgrade_info['price_display']} to unlock more features")
            if st.button("View Upgrade Options"):
                st.session_state.show_pricing = True
                st.rerun()
    
    def show_billing_history(self):
        """Display billing history (mock for now)"""
        if not st.session_state.get('logged_in', False):
            st.info("Login to view billing history")
            return
        
        st.markdown("### 💰 Billing History")
        
        # Mock billing data
        billing_data = [
            {"date": "2024-01-15", "amount": "$19.99", "plan": "Professional", "status": "Paid"},
            {"date": "2023-12-15", "amount": "$19.99", "plan": "Professional", "status": "Paid"},
            {"date": "2023-11-15", "amount": "$9.99", "plan": "Basic", "status": "Paid"}
        ]
        
        for record in billing_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(record["date"])
            with col2:
                st.write(record["amount"])
            with col3:
                st.write(record["plan"])
            with col4:
                status_color = "green" if record["status"] == "Paid" else "red"
                st.markdown(f"<span style='color: {status_color}'>{record['status']}</span>", unsafe_allow_html=True)
    
    def check_feature_access(self, feature_key: str, show_upgrade_prompt: bool = True) -> bool:
        """Check feature access and show upgrade prompt if needed"""
        current_plan = PaymentPlans.get_user_plan()
        has_access = PaymentPlans.can_access_feature(feature_key, current_plan)
        
        if not has_access and show_upgrade_prompt:
            upgrade_plan = PaymentPlans.get_upgrade_suggestion(current_plan)
            if upgrade_plan:
                upgrade_info = PaymentPlans.get_plan_info(upgrade_plan)
                st.warning(f"This feature requires {upgrade_info['name']} plan ({upgrade_info['price_display']})")
                if st.button("Upgrade Now", key=f"upgrade_{feature_key}"):
                    st.session_state.show_pricing = True
                    st.rerun()
        
        return has_access
    
    def check_daily_limit(self, show_upgrade_prompt: bool = True) -> bool:
        """Check daily usage limit and show upgrade prompt if needed"""
        can_analyze = PaymentPlans.check_daily_limit()
        
        if not can_analyze and show_upgrade_prompt:
            current_plan = PaymentPlans.get_user_plan()
            limits = PaymentPlans.get_usage_limits(current_plan)
            
            st.error(f"Daily limit reached ({limits['daily_analyses']} analyses)")
            st.info("Upgrade to Basic plan for unlimited daily analyses")
            if st.button("Upgrade Now", key="upgrade_daily_limit"):
                st.session_state.show_pricing = True
                st.rerun()
        
        return can_analyze

def show_payment_success():
    """Show payment success message"""
    st.success("🎉 Payment successful! Your subscription is now active.")
    st.balloons()
    
    # Get plan from URL parameters
    plan_id = st.query_params.get('plan', 'basic')
    st.session_state.user_plan = plan_id
    
    plan_info = PaymentPlans.get_plan_info(plan_id)
    st.info(f"Welcome to {plan_info['name']} plan! You now have access to all features.")

def show_payment_canceled():
    """Show payment canceled message"""
    st.warning("Payment was canceled. You can try again anytime.")
    st.info("Your current plan remains unchanged.")