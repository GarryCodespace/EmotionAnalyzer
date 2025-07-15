"""
Payment Plans Configuration for Emoticon App
Defines subscription tiers and pricing structure
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PaymentPlans:
    """Payment plans configuration and management"""
    
    PLANS = {
        'free': {
            'name': 'Free',
            'price': 0,
            'price_display': 'Free',
            'features': [
                'Basic emotion analysis',
                'Image upload analysis',
                'Video upload analysis',
                'Demo mode access',
                'Limited to 5 analyses per day'
            ],
            'limits': {
                'daily_analyses': 5,
                'save_history': False,
                'lie_detector': False,
                'advanced_features': False,
                'api_access': False
            },
            'stripe_price_id': None,
            'recommended': False
        },
        'basic': {
            'name': 'Basic',
            'price': 9.99,
            'price_display': '$9.99/month',
            'features': [
                'Unlimited emotion analysis',
                'Save analysis history',
                'Advanced AI insights',
                'Priority support',
                'Export analysis data'
            ],
            'limits': {
                'daily_analyses': -1,  # unlimited
                'save_history': True,
                'lie_detector': False,
                'advanced_features': True,
                'api_access': False
            },
            'stripe_price_id': 'price_basic_monthly',
            'recommended': True
        },
        'pro': {
            'name': 'Professional',
            'price': 19.99,
            'price_display': '$19.99/month',
            'features': [
                'Everything in Basic',
                'AI lie detector analysis',
                'Body language analysis',
                'Batch video processing',
                'API access',
                'Custom analysis models'
            ],
            'limits': {
                'daily_analyses': -1,
                'save_history': True,
                'lie_detector': True,
                'advanced_features': True,
                'api_access': True
            },
            'stripe_price_id': 'price_pro_monthly',
            'recommended': False
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 49.99,
            'price_display': '$49.99/month',
            'features': [
                'Everything in Professional',
                'White-label solution',
                'Custom integrations',
                'Dedicated support',
                'Advanced analytics',
                'Team management'
            ],
            'limits': {
                'daily_analyses': -1,
                'save_history': True,
                'lie_detector': True,
                'advanced_features': True,
                'api_access': True
            },
            'stripe_price_id': 'price_enterprise_monthly',
            'recommended': False
        }
    }
    
    @staticmethod
    def get_user_plan(user_id: Optional[int] = None) -> str:
        """Get current user's plan from session state or database"""
        # Admin override for specific user
        if st.session_state.get('user_email') == 'garryyuan1@gmail.com':
            st.session_state.user_plan = 'pro'
            return 'pro'
        
        if user_id and st.session_state.get('logged_in', False):
            # In production, this would query the database
            return st.session_state.get('user_plan', 'free')
        return 'free'
    
    @staticmethod
    def get_plan_info(plan_name: str) -> Dict:
        """Get information about a specific plan"""
        return PaymentPlans.PLANS.get(plan_name, PaymentPlans.PLANS['free'])
    
    @staticmethod
    def can_access_feature(feature: str, user_plan: str = None) -> bool:
        """Check if user can access a specific feature"""
        if user_plan is None:
            user_plan = PaymentPlans.get_user_plan()
        
        plan_info = PaymentPlans.get_plan_info(user_plan)
        return plan_info['limits'].get(feature, False)
    
    @staticmethod
    def get_usage_limits(user_plan: str = None) -> Dict:
        """Get usage limits for current user plan"""
        if user_plan is None:
            user_plan = PaymentPlans.get_user_plan()
        
        plan_info = PaymentPlans.get_plan_info(user_plan)
        return plan_info['limits']
    
    @staticmethod
    def check_daily_limit(user_id: Optional[int] = None) -> bool:
        """Check if user has reached daily analysis limit"""
        user_plan = PaymentPlans.get_user_plan(user_id)
        limits = PaymentPlans.get_usage_limits(user_plan)
        
        daily_limit = limits['daily_analyses']
        if daily_limit == -1:  # unlimited
            return True
        
        # Check current usage from session state
        # In production, this would check database
        today_usage = st.session_state.get('daily_usage', 0)
        return today_usage < daily_limit
    
    @staticmethod
    def increment_usage():
        """Increment daily usage counter"""
        if 'daily_usage' not in st.session_state:
            st.session_state.daily_usage = 0
        st.session_state.daily_usage += 1
    
    @staticmethod
    def reset_daily_usage():
        """Reset daily usage counter (call at midnight)"""
        st.session_state.daily_usage = 0
    
    @staticmethod
    def get_upgrade_suggestion(current_plan: str) -> Optional[str]:
        """Get suggested upgrade plan"""
        plan_hierarchy = ['free', 'basic', 'pro', 'enterprise']
        try:
            current_index = plan_hierarchy.index(current_plan)
            if current_index < len(plan_hierarchy) - 1:
                return plan_hierarchy[current_index + 1]
        except ValueError:
            pass
        return None

class UsageTracker:
    """Track usage for billing and limits"""
    
    @staticmethod
    def track_analysis(analysis_type: str, user_id: Optional[int] = None):
        """Track an analysis for billing purposes"""
        if 'usage_log' not in st.session_state:
            st.session_state.usage_log = []
        
        usage_entry = {
            'type': analysis_type,
            'timestamp': datetime.now(),
            'user_id': user_id,
            'plan': PaymentPlans.get_user_plan(user_id)
        }
        
        st.session_state.usage_log.append(usage_entry)
        PaymentPlans.increment_usage()
    
    @staticmethod
    def get_usage_stats(user_id: Optional[int] = None) -> Dict:
        """Get usage statistics for current user"""
        if 'usage_log' not in st.session_state:
            return {'total': 0, 'today': 0, 'this_week': 0, 'this_month': 0}
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        usage_log = st.session_state.usage_log
        
        stats = {
            'total': len(usage_log),
            'today': len([u for u in usage_log if u['timestamp'] >= today_start]),
            'this_week': len([u for u in usage_log if u['timestamp'] >= week_start]),
            'this_month': len([u for u in usage_log if u['timestamp'] >= month_start])
        }
        
        return stats