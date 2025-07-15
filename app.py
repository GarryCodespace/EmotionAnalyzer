import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import uuid
import tempfile
import os
from datetime import datetime
from openai_analyzer import analyze_expression
from database import init_database, save_emotion_analysis, get_user_history, get_expression_statistics
from video_analyzer import VideoEmotionAnalyzer
from body_language_analyzer import BodyLanguageAnalyzer
from lie_detector import LieDetector
from ai_vision_analyzer import AIVisionAnalyzer
from stress_analyzer import StressAnalyzer
from login_ui import require_authentication, show_user_menu, show_account_settings, init_auth_session, logout_user, show_login_modal, auto_login
import login_ui
from payment_ui import PaymentUI, check_daily_limit
from payment_plans import PaymentPlans, UsageTracker

# Setup MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5, refine_landmarks=True)

# Initialize analyzers
body_analyzer = BodyLanguageAnalyzer()
lie_detector = LieDetector()
ai_vision = AIVisionAnalyzer()
stress_analyzer = StressAnalyzer()
payment_ui = PaymentUI()

# Define 100+ gestures (some with reduced sensitivity thresholds)
GESTURES = [
    ("raised left eyebrow", lambda lm: (lm[159].y - lm[65].y) > 0.06),
    ("raised right eyebrow", lambda lm: (lm[386].y - lm[295].y) > 0.06),
    ("mouth open", lambda lm: abs(lm[13].y - lm[14].y) > 0.05),
    ("frown", lambda lm: abs(lm[61].x - lm[291].x) < 0.035),
    ("pursed lips", lambda lm: abs(lm[61].x - lm[291].x) < 0.025),
    ("smirk left", lambda lm: lm[61].y > lm[291].y + 0.015),
    ("smirk right", lambda lm: lm[291].y > lm[61].y + 0.015),
    ("cheek puff", lambda lm: abs(lm[50].x - lm[280].x) > 0.25),
    ("nostril flare", lambda lm: abs(lm[94].x - lm[331].x) > 0.05),
    ("lip bite", lambda lm: abs(lm[13].y - lm[14].y) < 0.008 and abs(lm[61].x - lm[291].x) < 0.01),
    ("brow furrow", lambda lm: abs(lm[65].x - lm[295].x) < 0.03),
    ("brow lift", lambda lm: (lm[65].y + lm[295].y) / 2 < lm[10].y - 0.03),
    ("eye roll up", lambda lm: lm[468].y < lm[474].y - 0.02),
    ("eye roll down", lambda lm: lm[468].y > lm[474].y + 0.02),
    ("chin thrust forward", lambda lm: lm[152].z < -0.1),
    ("chin tuck", lambda lm: lm[152].z > 0.1),
    ("eye blink left", lambda lm: abs(lm[159].y - lm[145].y) < 0.005),
    ("eye blink right", lambda lm: abs(lm[386].y - lm[374].y) < 0.005),
    ("eyes wide open", lambda lm: abs(lm[159].y - lm[145].y) > 0.035),
    ("glare left", lambda lm: lm[33].x - lm[133].x > 0.02),
    ("glare right", lambda lm: lm[263].x - lm[362].x > 0.02),
    ("glare up", lambda lm: (lm[159].y + lm[386].y)/2 < (lm[145].y + lm[374].y)/2 - 0.02),
    ("glare down", lambda lm: (lm[159].y + lm[386].y)/2 > (lm[145].y + lm[374].y)/2 + 0.02),
    ("brows raised and mouth open", lambda lm: (lm[159].y - lm[65].y) > 0.03 and abs(lm[13].y - lm[14].y) > 0.04),
    ("brows lowered and lips pressed", lambda lm: (lm[159].y - lm[65].y) < 0.01 and abs(lm[13].y - lm[14].y) < 0.01),
    ("eye squint left", lambda lm: abs(lm[159].y - lm[145].y) < 0.007),
    ("eye squint right", lambda lm: abs(lm[386].y - lm[374].y) < 0.007),
    ("jaw drop", lambda lm: abs(lm[152].y - lm[13].y) > 0.15),
    ("head tilt left", lambda lm: lm[234].y - lm[454].y > 0.03),
    ("head tilt right", lambda lm: lm[454].y - lm[234].y > 0.03),
    ("head turn right", lambda lm: lm[454].x < lm[234].x - 0.05),
    ("head turn down", lambda lm: lm[10].y > lm[152].y + 0.08), 
    ("nose wrinkle", lambda lm: abs(lm[6].y - lm[168].y) < 0.02),
    ("brow raise + smile", lambda lm: (lm[159].y - lm[65].y) > 0.1 and abs(lm[61].x - lm[291].x) > 0.08),
    ("brow furrow + frown", lambda lm: abs(lm[65].x - lm[295].x) < 0.03 and abs(lm[61].x - lm[291].x) < 0.035),
    ("mouth open + head tilt", lambda lm: abs(lm[13].y - lm[14].y) > 0.04 and abs(lm[234].y - lm[454].y) > 0.03),
    # Additional gestures to reach 100+
    ("subtle smile", lambda lm: abs(lm[61].x - lm[291].x) > 0.04 and abs(lm[61].x - lm[291].x) < 0.06),
    ("wide smile", lambda lm: abs(lm[61].x - lm[291].x) > 0.08),
    ("half smile left", lambda lm: lm[61].x > lm[291].x + 0.02),
    ("half smile right", lambda lm: lm[291].x > lm[61].x + 0.02),
    ("lip compression", lambda lm: abs(lm[13].y - lm[14].y) < 0.003),
    ("lip protrusion", lambda lm: lm[13].z < -0.02),
    ("mouth corner down left", lambda lm: lm[61].y > lm[13].y + 0.01),
    ("mouth corner down right", lambda lm: lm[291].y > lm[13].y + 0.01),
    ("mouth corner up left", lambda lm: lm[61].y < lm[13].y - 0.01),
    ("mouth corner up right", lambda lm: lm[291].y < lm[13].y - 0.01),
    ("upper lip raise", lambda lm: lm[12].y < lm[15].y - 0.01),
    ("lower lip depress", lambda lm: lm[15].y > lm[17].y + 0.01),
    ("cheek raise left", lambda lm: lm[116].y < lm[117].y - 0.01),
    ("cheek raise right", lambda lm: lm[345].y < lm[346].y - 0.01),
    ("eye narrow left", lambda lm: abs(lm[159].y - lm[145].y) < 0.01),
    ("eye narrow right", lambda lm: abs(lm[386].y - lm[374].y) < 0.01),
    ("eye widen left", lambda lm: abs(lm[159].y - lm[145].y) > 0.025),
    ("eye widen right", lambda lm: abs(lm[386].y - lm[374].y) > 0.025),
    ("eyebrow flash", lambda lm: (lm[159].y - lm[65].y) > 0.08),
    ("forehead furrow", lambda lm: abs(lm[10].y - lm[151].y) < 0.08),
    ("temple tension", lambda lm: abs(lm[162].x - lm[389].x) < 0.15),
    ("jaw clench", lambda lm: abs(lm[172].y - lm[397].y) < 0.02),
    ("mouth twist left", lambda lm: lm[61].x < lm[291].x - 0.03),
    ("mouth twist right", lambda lm: lm[291].x < lm[61].x - 0.03),
    ("nostril compress", lambda lm: abs(lm[94].x - lm[331].x) < 0.03),
    ("nostril dilate", lambda lm: abs(lm[94].x - lm[331].x) > 0.06),
    ("chin dimple", lambda lm: lm[175].y > lm[199].y + 0.01),
    ("chin raise", lambda lm: lm[175].y < lm[199].y - 0.01),
    ("head shake", lambda lm: abs(lm[234].x - lm[454].x) > 0.1),
    ("head nod", lambda lm: abs(lm[10].y - lm[152].y) > 0.12),
    ("ear wiggle left", lambda lm: lm[234].z > 0.05),
    ("ear wiggle right", lambda lm: lm[454].z > 0.05),
    ("eye flutter left", lambda lm: abs(lm[159].y - lm[145].y) < 0.003),
    ("eye flutter right", lambda lm: abs(lm[386].y - lm[374].y) < 0.003),
    ("micro smile", lambda lm: abs(lm[61].x - lm[291].x) > 0.025 and abs(lm[61].x - lm[291].x) < 0.035),
    ("micro frown", lambda lm: abs(lm[61].x - lm[291].x) < 0.02),
    ("eyebrow twitch left", lambda lm: (lm[159].y - lm[65].y) > 0.04 and (lm[159].y - lm[65].y) < 0.05),
    ("eyebrow twitch right", lambda lm: (lm[386].y - lm[295].y) > 0.04 and (lm[386].y - lm[295].y) < 0.05),
    ("lip twitch left", lambda lm: lm[61].y < lm[291].y - 0.005),
    ("lip twitch right", lambda lm: lm[291].y < lm[61].y - 0.005),
    ("eye contact direct", lambda lm: abs(lm[468].x - lm[473].x) < 0.01),
    ("eye contact avoidance", lambda lm: abs(lm[468].x - lm[473].x) > 0.03),
    ("pupil dilation", lambda lm: abs(lm[468].y - lm[473].y) > 0.02),
    ("pupil constriction", lambda lm: abs(lm[468].y - lm[473].y) < 0.005),
    ("surprise full", lambda lm: (lm[159].y - lm[65].y) > 0.07 and abs(lm[13].y - lm[14].y) > 0.06),
    ("disgust expression", lambda lm: lm[12].y < lm[15].y - 0.02 and abs(lm[6].y - lm[168].y) < 0.015),
    ("fear expression", lambda lm: abs(lm[159].y - lm[145].y) > 0.03 and (lm[159].y - lm[65].y) > 0.05),
    ("anger expression", lambda lm: abs(lm[65].x - lm[295].x) < 0.025 and abs(lm[61].x - lm[291].x) < 0.03),
    ("sadness expression", lambda lm: lm[61].y > lm[13].y + 0.015 and lm[291].y > lm[13].y + 0.015),
    ("contempt left", lambda lm: lm[61].y < lm[291].y - 0.02),
    ("contempt right", lambda lm: lm[291].y < lm[61].y - 0.02),
    ("stress indicators", lambda lm: abs(lm[65].x - lm[295].x) < 0.025 and abs(lm[172].y - lm[397].y) < 0.015),
    ("relaxed expression", lambda lm: abs(lm[159].y - lm[145].y) > 0.015 and abs(lm[13].y - lm[14].y) > 0.01),
    ("concentration", lambda lm: abs(lm[65].x - lm[295].x) < 0.035 and abs(lm[159].y - lm[145].y) < 0.012),
    ("confusion", lambda lm: (lm[159].y - lm[65].y) > 0.03 and (lm[386].y - lm[295].y) < 0.02),
    ("skepticism", lambda lm: (lm[159].y - lm[65].y) > 0.04 and abs(lm[61].x - lm[291].x) < 0.025),
    ("amusement", lambda lm: abs(lm[61].x - lm[291].x) > 0.06 and abs(lm[159].y - lm[145].y) < 0.015),
    ("boredom", lambda lm: abs(lm[159].y - lm[145].y) < 0.008 and abs(lm[13].y - lm[14].y) < 0.005),
    ("excitement", lambda lm: abs(lm[159].y - lm[145].y) > 0.025 and abs(lm[61].x - lm[291].x) > 0.07),
    ("determination", lambda lm: abs(lm[65].x - lm[295].x) < 0.03 and abs(lm[172].y - lm[397].y) < 0.02),
    ("nervousness", lambda lm: abs(lm[159].y - lm[145].y) < 0.006 and lm[61].y > lm[291].y + 0.01),
    ("confidence", lambda lm: lm[152].z < -0.05 and abs(lm[61].x - lm[291].x) > 0.05),
    ("insecurity", lambda lm: lm[152].z > 0.05 and abs(lm[234].y - lm[454].y) > 0.025),
    ("thoughtfulness", lambda lm: abs(lm[65].x - lm[295].x) < 0.04 and lm[13].y > lm[14].y + 0.02),
    ("disbelief", lambda lm: (lm[159].y - lm[65].y) > 0.05 and abs(lm[13].y - lm[14].y) > 0.03),
    ("empathy", lambda lm: abs(lm[61].x - lm[291].x) > 0.04 and abs(lm[159].y - lm[145].y) > 0.02),
    ("curiosity", lambda lm: (lm[159].y - lm[65].y) > 0.045 and lm[10].y < lm[152].y - 0.06),
    ("anticipation", lambda lm: abs(lm[159].y - lm[145].y) > 0.02 and abs(lm[13].y - lm[14].y) > 0.02),
    ("relief", lambda lm: abs(lm[61].x - lm[291].x) > 0.05 and abs(lm[159].y - lm[145].y) > 0.015),
    ("frustration", lambda lm: abs(lm[65].x - lm[295].x) < 0.025 and abs(lm[13].y - lm[14].y) < 0.006),
    ("affection", lambda lm: abs(lm[61].x - lm[291].x) > 0.06 and abs(lm[159].y - lm[145].y) > 0.018),
    ("pride", lambda lm: lm[152].z < -0.08 and abs(lm[61].x - lm[291].x) > 0.055),
    ("embarrassment", lambda lm: lm[10].y > lm[152].y + 0.05 and abs(lm[159].y - lm[145].y) < 0.01),
    ("guilt", lambda lm: lm[10].y > lm[152].y + 0.06 and abs(lm[61].x - lm[291].x) < 0.02),
    ("jealousy", lambda lm: abs(lm[65].x - lm[295].x) < 0.02 and lm[61].y > lm[291].y + 0.02),
    ("envy", lambda lm: abs(lm[159].y - lm[145].y) < 0.008 and abs(lm[65].x - lm[295].x) < 0.03),
    ("longing", lambda lm: abs(lm[159].y - lm[145].y) > 0.02 and abs(lm[13].y - lm[14].y) > 0.015),
    ("nostalgia", lambda lm: abs(lm[61].x - lm[291].x) > 0.04 and lm[10].y > lm[152].y + 0.03),
    ("melancholy", lambda lm: lm[61].y > lm[13].y + 0.02 and abs(lm[159].y - lm[145].y) < 0.012),
    ("serenity", lambda lm: abs(lm[159].y - lm[145].y) > 0.018 and abs(lm[13].y - lm[14].y) > 0.008),
    ("euphoria", lambda lm: abs(lm[61].x - lm[291].x) > 0.09 and abs(lm[159].y - lm[145].y) > 0.03),
    ("despair", lambda lm: lm[61].y > lm[13].y + 0.025 and abs(lm[159].y - lm[145].y) < 0.005),
    ("hope", lambda lm: abs(lm[61].x - lm[291].x) > 0.045 and (lm[159].y - lm[65].y) > 0.035),
    ("resignation", lambda lm: abs(lm[159].y - lm[145].y) < 0.01 and abs(lm[13].y - lm[14].y) < 0.008),
    ("defiance", lambda lm: lm[152].z < -0.06 and abs(lm[65].x - lm[295].x) < 0.025),
    ("submission", lambda lm: lm[10].y > lm[152].y + 0.04 and abs(lm[159].y - lm[145].y) < 0.008),
    ("dominance", lambda lm: lm[152].z < -0.07 and abs(lm[159].y - lm[145].y) < 0.01),
    ("vulnerability", lambda lm: abs(lm[159].y - lm[145].y) > 0.025 and lm[10].y > lm[152].y + 0.03),
    ("strength", lambda lm: abs(lm[172].y - lm[397].y) < 0.015 and lm[152].z < -0.04),
    ("weakness", lambda lm: lm[10].y > lm[152].y + 0.05 and abs(lm[172].y - lm[397].y) > 0.03),
    ("alertness", lambda lm: abs(lm[159].y - lm[145].y) > 0.022 and (lm[159].y - lm[65].y) > 0.03),
    ("drowsiness", lambda lm: abs(lm[159].y - lm[145].y) < 0.006 and lm[10].y > lm[152].y + 0.02),
    ("intensity", lambda lm: abs(lm[159].y - lm[145].y) < 0.01 and abs(lm[65].x - lm[295].x) < 0.02),
    ("gentleness", lambda lm: abs(lm[61].x - lm[291].x) > 0.04 and abs(lm[159].y - lm[145].y) > 0.015)
]

# Global state for tracking detections
last_detected = set()
last_detect_time = {}
cooldown_seconds = 5

st.set_page_config(page_title="Emoticon – Emotion Detector", layout="wide")

# Force light theme


# Initialize projects data


# Apply light theme
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #000000;
}
.stButton > button {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #ccc;
}
.stButton > button:hover {
    background-color: #e0e0e0;
    border: 1px solid #aaa;
}
.stSelectbox > div > div {
    background-color: #f8f8f8;
    color: #000000;
    border: 1px solid #ddd;
}
.stTextInput > div > div > input {
    background-color: #f8f8f8;
    color: #000000;
    border: 1px solid #ddd;
}

/* Change yellow alert/warning boxes to blue */
div[data-testid="stAlert"] > div {
    background-color: #e3f2fd;
    border: 1px solid #90caf9;
    color: #1565c0;
}
div[data-testid="stSuccess"] > div {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}
div[data-testid="stError"] > div {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
div[data-testid="stInfo"] > div {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
}

/* Capitalize sidebar navigation items */
.css-1d391kg p {
    text-transform: capitalize;
}

/* Alternative selector for sidebar navigation */
[data-testid="stSidebar"] .css-1d391kg p {
    text-transform: capitalize;
}

/* More specific selector for navigation items */
.css-1d391kg p:first-child {
    text-transform: capitalize;
}

/* Target nav links in sidebar */
.css-1d391kg a {
    text-transform: capitalize;
}

/* Target navigation labels */
.css-1d391kg span {
    text-transform: capitalize;
}

/* General sidebar navigation capitalization */
[data-testid="stSidebar"] ul li a {
    text-transform: capitalize;
}

.stMarkdown {
    color: #000000 !important;
}
.stText {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# Top navigation menu
st.markdown("""
<style>
.nav-container {
    background-color: #1f1f1f;
    padding: 15px 0;
    margin: -1rem -1rem 2rem -1rem;
    border-bottom: 1px solid #333;
}
.nav-menu {
    display: flex;
    justify-content: center;
    gap: 40px;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}
.nav-item {
    color: #ffffff;
    text-decoration: none;
    font-size: 16px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 4px;
    transition: all 0.3s ease;
    cursor: pointer;
}
.nav-item:link, .nav-item:visited {
    text-decoration: none;
    color: #ffffff;
}
.nav-item:hover {
    background-color: #333;
    color: #ffffff;
}
.nav-item.active {
    background-color: #0066cc;
    color: #ffffff;
}
</style>
<div class="nav-container">
    <div class="nav-menu">
        <span class="nav-item active">Home</span>
        <span class="nav-item">About</span>
        <span class="nav-item">Contact</span>
        <span class="nav-item">Screen Recorder</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation functionality using columns - styled buttons
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 1, 1, 1])

with nav_col1:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")

with nav_col2:
    if st.button("About", key="nav_about", use_container_width=True):
        st.switch_page("pages/about.py")

with nav_col3:
    if st.button("Pricing", key="nav_pricing", use_container_width=True):
        st.switch_page("pages/pricing.py")

with nav_col4:
    if st.button("Contact", key="nav_contact", use_container_width=True):
        st.switch_page("pages/contact.py")

with nav_col5:
    if st.button("Career", key="nav_career", use_container_width=True):
        st.switch_page("pages/career.py")

# Style the navigation buttons to match the design
st.markdown("""
<style>
/* Style navigation buttons */
[data-testid="stColumns"] [data-testid="stButton"] > button {
    background-color: #1f1f1f !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    font-size: 16px;
    font-weight: 500;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
}

/* Remove focus outline */
[data-testid="stColumns"] [data-testid="stButton"] > button:focus {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
}

/* Active state for home button */
[data-testid="stColumns"] [data-testid="stButton"]:first-child > button {
    background-color: #0066cc;
    color: #ffffff;
}

/* Hover effects */
[data-testid="stColumns"] [data-testid="stButton"] > button:hover {
    background-color: #0066cc;
    color: #ffffff;
}

/* Remove the visual navigation bar since we're using real buttons now */
.nav-container {
    display: none;
}
</style>
""", unsafe_allow_html=True)







# Header with logo and login/theme toggle
header_col1, header_col2, header_col3 = st.columns([2, 6, 2])
with header_col1:
    st.markdown("<br><br>", unsafe_allow_html=True)  # Push logo down to align with subtitle
    
    # Logo display
    try:
        st.image("logo.png", width=120)
    except:
        st.markdown("🎭", unsafe_allow_html=True)
    

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Reduce spacing for closer text
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<h1 style='font-size: 3rem; margin: 0; margin-bottom: -35px;'>Emoticon</h1>", unsafe_allow_html=True)
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<p style='margin-top: -35px;'>Live AI Emotion Interpretation from Micro-Expressions</p>", unsafe_allow_html=True)
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<p style='margin-top: -10px; font-size: 0.9rem; color: #666;'>Try it now - Upload an image to experience AI emotion analysis</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    
    # Login/User menu in top right
    if st.session_state.get('logged_in', False):
        user_email = st.session_state.get('user_email', 'User')
        user_name = user_email.split('@')[0].title()
        
        # User dropdown menu
        with st.popover(f"👤 {user_name}"):
            st.markdown(f"**{user_email}**")
            st.markdown("---")
            if st.button("Account Settings", key="account_settings_btn", use_container_width=True):
                st.session_state.show_account_settings = True
                st.rerun()
            if st.button("Logout", key="logout_btn", use_container_width=True):
                logout_user()
    else:
        if st.button("Log in", key="login_btn"):
            st.session_state.show_login_modal = True
            st.rerun()
    


# Initialize database
try:
    init_database()
except Exception as e:
    st.error(f"❌ Database connection issue: {str(e)}")

# Initialize auth session and auto-login
init_auth_session()
auto_login_success = auto_login()

# Show welcome message for auto-login (only once per session)
if auto_login_success and st.session_state.get('logged_in', False) and not st.session_state.get('welcome_shown', False):
    user_email = st.session_state.get('user_email', 'User')
    st.info(f"Welcome back, {user_email}! You're automatically logged in for 30 days.")
    st.session_state.welcome_shown = True

# Show account settings if requested
if st.session_state.get('show_account_settings', False):
    show_account_settings()
    st.stop()

# Show login modal if requested
if st.session_state.get('show_login_modal', False):
    show_login_modal()
    st.stop()

# API Key Status Check
try:
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OpenAI API key not found")
except Exception as e:
    st.error(f"❌ OpenAI connection issue: {str(e)}")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def analyze_uploaded_image(uploaded_file):
    """Analyze the uploaded image"""
    # Check daily usage limit
    if not payment_ui.check_daily_limit():
        st.stop()
    
    # Display uploaded image
    uploaded_file.seek(0)  # Reset file pointer
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Track usage
    UsageTracker.track_analysis("image", st.session_state.get('user_id'))
    
    # Process image with AI vision analysis
    with st.spinner('Analyzing image with AI vision...'):
        # Get context if provided
        context = st.session_state.get('analysis_context', '')
        if context:
            ai_analysis = ai_vision.analyze_emotion_context(image, [context])
        else:
            ai_analysis = ai_vision.analyze_facial_expressions(image)
    
    # Extract analysis results
    detected_expressions = ai_analysis.get("facial_expressions", [])
    detected_body_language = ai_analysis.get("body_language", [])
    emotional_state = ai_analysis.get("emotional_state", "neutral")
    confidence_level = ai_analysis.get("confidence_level", "medium")
    detailed_analysis = ai_analysis.get("detailed_analysis", "")
    
    # Display AI analysis summary
    st.success(f"**AI Vision Analysis Complete** - Confidence: {confidence_level.title()}")
    
    # Display emotional state
    if emotional_state and emotional_state != "neutral":
        st.info(f"**Primary Emotional State**: {emotional_state.title()}")
    
    # Display detailed analysis
    if detailed_analysis:
        st.markdown(f"**AI Analysis**: {detailed_analysis}")
    
    # Display body language analysis
    if detected_body_language:
        st.success(f"**Body Language Patterns Detected**: {len(detected_body_language)}")
        
        body_col1, body_col2 = st.columns(2)
        for idx, pattern in enumerate(detected_body_language[:8]):
            pattern_text = f"{pattern.title()}"
            
            if idx % 2 == 0:
                body_col1.markdown(f"• {pattern_text}")
            else:
                body_col2.markdown(f"• {pattern_text}")
        
        # Create body patterns for compatibility
        body_patterns = [
            {'pattern': pattern.replace(' ', '_'), 'confidence': 0.8}
            for pattern in detected_body_language
        ]
    else:
        st.info("**Body Language**: No significant body language patterns detected")
        body_patterns = []
    
    # Display facial expressions from AI analysis
    if detected_expressions:
        st.success(f"**Facial Expressions Detected**: {len(detected_expressions)}")
        
        expr_col1, expr_col2 = st.columns(2)
        confidence_scores = ai_vision.get_expression_confidence(detected_expressions)
        
        for idx, expr in enumerate(detected_expressions[:8]):
            expression_text = f"{expr.title()}"
            confidence = confidence_scores.get(expr, 0.0)
            
            if idx % 2 == 0:
                expr_col1.markdown(f"• {expression_text} ({confidence:.0%})")
            else:
                expr_col2.markdown(f"• {expression_text} ({confidence:.0%})")
    else:
        st.info("**Facial Expressions**: No significant expressions detected")
    
    # Deception Analysis (Premium Feature)
    st.markdown("### Deception Analysis")
    
    # Check if user has access to lie detector
    if not payment_ui.check_feature_access('lie_detector'):
        st.warning("Lie detector analysis requires Professional plan or higher")
    elif not PaymentPlans.check_lie_detection_limit():
        st.error("Daily lie detection limit reached (1 per day)")
        st.info("Upgrade to Professional for unlimited lie detections")
        if st.button("Upgrade to Professional", key="upgrade_lie_unlimited"):
            st.switch_page("pages/billing.py")
    else:
        # Run lie detector analysis
        deception_analysis = lie_detector.analyze_deception(detected_expressions, body_patterns)
        
        # Increment lie detection usage
        PaymentPlans.increment_lie_detection()
        
        deception_probability = deception_analysis.get('deception_probability', 0.0)
        confidence_level = deception_analysis.get('confidence_level', 'Low')
        key_indicators = deception_analysis.get('key_indicators', [])
        
        # Display deception probability with color coding
        if deception_probability >= 0.7:
            st.error(f"**Deception Risk**: HIGH ({deception_probability:.1%}) - Confidence: {confidence_level}")
        elif deception_probability >= 0.4:
            st.warning(f"**Deception Risk**: MEDIUM ({deception_probability:.1%}) - Confidence: {confidence_level}")
        else:
            st.success(f"**Deception Risk**: LOW ({deception_probability:.1%}) - Confidence: {confidence_level}")
        
        # Display key indicators
        if key_indicators:
            st.markdown("**Key Deception Indicators:**")
            for indicator in key_indicators[:5]:
                st.markdown(f"• {indicator}")
        
        # Get AI interpretation
        ai_interpretation = deception_analysis.get('ai_interpretation', '')
        if ai_interpretation:
            st.markdown("**AI Deception Analysis:**")
            st.markdown(ai_interpretation)
    
    # Stress Analysis (Premium Feature)
    st.markdown("### Stress & Anxiety Level")
    
    # Check if user has access to stress detector
    if not payment_ui.check_feature_access('stress_detector'):
        st.warning("Stress Analysis requires Professional plan or higher")
    elif not PaymentPlans.check_stress_detection_limit():
        st.error("Daily stress detection limit reached (1 per day)")
        st.info("Upgrade to Professional for unlimited stress analysis")
        if st.button("Upgrade to Professional", key="upgrade_stress_unlimited"):
            st.switch_page("pages/billing.py")
    else:
        # Run stress analysis
        stress_analysis = stress_analyzer.analyze_stress_level(image)
        
        # Increment stress detection usage
        PaymentPlans.increment_stress_detection()
        
        # Display stress level
        stress_percentage = stress_analysis['stress_percentage']
        stress_level = stress_analysis['stress_level']
        stress_color = stress_analysis['stress_color']
        
        st.markdown(f"**Stress Level**: <span style='color: {stress_color}; font-weight: bold;'>You look {stress_percentage}% stressed ({stress_level})</span>", 
                   unsafe_allow_html=True)
        
        # Show stress indicators
        if stress_analysis.get('indicators'):
            st.markdown("**Stress Indicators:**")
            for indicator in stress_analysis['indicators'][:4]:
                st.markdown(f"• {indicator.replace('_', ' ').title()}")
        
        # Show recommendations
        if stress_analysis.get('recommendations'):
            st.markdown("**Recommendations:**")
            for rec in stress_analysis['recommendations'][:3]:
                st.markdown(f"• {rec}")
    
    # Save analysis to database only if logged in
    if st.session_state.get('logged_in', False):
        try:
            expressions_json = json.dumps(detected_expressions) if detected_expressions else "[]"
            save_emotion_analysis(
                st.session_state.session_id,
                detected_expressions,
                detailed_analysis,
                "image",
                0.0
            )
            st.success("Analysis saved to history")
        except Exception as e:
            st.error(f"Could not save analysis: {str(e)}")
    else:
        st.info("💡 Login to save analysis history and access advanced features")
        if st.button("Login to Save History", key="login_for_image_save"):
            st.session_state.show_login_modal = True
            st.rerun()

# Popular Use Cases Section
st.markdown("---")
st.markdown("### Popular Use Cases")
st.markdown("*Describe your specific scenario for better analysis*")

# Create columns for use case examples
case_col1, case_col2, case_col3, case_col4 = st.columns(4)

with case_col1:
    if st.button("😄 For Fun\nAnalyze photos with friends", key="fun_case", use_container_width=True):
        st.session_state.analysis_context = "I'm having fun analyzing photos with friends to see what our facial expressions reveal about our personalities and emotions during social moments."
        st.rerun()

with case_col2:
    if st.button("💼 Interview\nAssess candidates", key="interview_case", use_container_width=True):
        st.session_state.analysis_context = "I'm analyzing an interview video to assess the candidate's confidence level, honesty, and stress indicators during the hiring process."
        st.rerun()

with case_col3:
    if st.button("💕 Date\nRead emotions", key="date_case", use_container_width=True):
        st.session_state.analysis_context = "I'm analyzing photos from a date to understand the person's genuine interest level and emotional state during our interaction."
        st.rerun()

with case_col4:
    if st.button("🔍 Interrogation\nDetect deception", key="interrogation_case", use_container_width=True):
        st.session_state.analysis_context = "I'm analyzing this person to detect deception indicators and assess truthfulness based on facial micro-expressions and body language."
        st.rerun()

# Context input for better analysis
st.markdown("### Describe Your Scenario")
context_input = st.text_area(
    "Tell us about your situation to get more personalized analysis:",
    value=st.session_state.get('analysis_context', ''),
    placeholder="Example: Job interview analysis for confidence and honesty assessment...",
    height=80,
    key="analysis_context_input"
)

if context_input:
    st.session_state.analysis_context = context_input
    st.success("Context saved! Your analysis will be tailored to this scenario.")

# Clear context button
if st.session_state.get('analysis_context'):
    if st.button("Clear Context", key="clear_context"):
        st.session_state.analysis_context = ""
        st.rerun()

# Add Analysis History to Sidebar
with st.sidebar:
    # Show usage statistics
    current_plan = PaymentPlans.get_user_plan()
    plan_info = PaymentPlans.get_plan_info(current_plan)
    usage_stats = UsageTracker.get_usage_stats()
    
    st.markdown(f"**Plan:** {plan_info['name']}")
    
    # Show daily usage limit
    limits = PaymentPlans.get_usage_limits(current_plan)
    daily_limit = limits['daily_analyses']
    if daily_limit == -1:
        st.markdown(f"**Usage:** {usage_stats['today']}/Unlimited today")
    else:
        st.markdown(f"**Usage:** {usage_stats['today']}/{daily_limit} today")
        if usage_stats['today'] >= daily_limit:
            st.error("Daily limit reached!")
    
    # Show billing link for logged in users
    if st.session_state.get('logged_in', False):
        if st.button("💳 Billing", key="billing_sidebar", use_container_width=True):
            st.switch_page("pages/billing.py")
    else:
        st.markdown("### Get Started")
        st.info("Create an account to save your analysis history and unlock premium features!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_sidebar", use_container_width=True):
                st.session_state.show_login_modal = True
                st.rerun()
        with col2:
            if st.button("Register", key="register_sidebar", use_container_width=True):
                st.session_state.show_login_modal = True
                st.session_state.show_register = True
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Try It Now")
        st.success("Upload an image below to experience AI emotion analysis!")
        
        # Show basic plan info
        st.markdown("### Current Plan")
        st.markdown("**Free Trial**: 5 analyses per day")
        
        # Show upgrade option
        if st.button("Upgrade Plan", key="upgrade_sidebar", use_container_width=True):
            st.switch_page("pages/pricing.py")

# Welcome message for new users
if not st.session_state.get('logged_in', False):
    st.markdown("---")
    st.markdown("### Try Emoticon Now - No Login Required!")
    
    # Show demo benefits
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**AI Vision Analysis**")
        st.markdown("Advanced facial expression detection")
    with col2:
        st.markdown("**Emotional Insights**")
        st.markdown("Psychological interpretation of expressions")
    with col3:
        st.markdown("**Instant Results**")
        st.markdown("Get analysis in seconds")

st.markdown("---")

# AI Tools Section
st.markdown("### AI Tools")

# Simple plus sign tools design
tools_col1, tools_col2, tools_col3, tools_col4 = st.columns(4)

with tools_col1:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 14px; font-weight: 600;">Upload Image</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕", key="upload_image_tool", use_container_width=True):
        st.session_state.show_upload_image = True
        st.rerun()

with tools_col2:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 14px; font-weight: 600;">Upload Video</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕", key="upload_video_tool", use_container_width=True):
        st.session_state.show_upload_video = True
        st.rerun()

with tools_col3:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 14px; font-weight: 600;">AI Lie Detector</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕", key="lie_detector_tool", use_container_width=True):
        st.session_state.show_lie_detector_tool = True
        st.rerun()

with tools_col4:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 14px; font-weight: 600;">Stress Analyzer</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕", key="stress_analyzer_tool", use_container_width=True):
        st.session_state.show_stress_analyzer_tool = True
        st.rerun()

# Second row of tools
tools_col5, tools_col6, tools_col7, tools_col8 = st.columns(4)

with tools_col5:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 14px; font-weight: 600;">Deception Level</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕", key="deception_level_tool", use_container_width=True):
        st.session_state.show_deception_level_tool = True
        st.rerun()



# Show upload interfaces when tools are activated
if st.session_state.get('show_upload_image', False):
    st.markdown("---")
    st.markdown("### Upload Image")
    
    # Hide drag-and-drop text with custom CSS
    st.markdown("""
    <style>
    .uploadedFile {
        display: none;
    }
    .css-1kyxreq {
        display: none;
    }
    .css-1eznxh6 {
        display: none;
    }
    .css-1pqgz65 {
        display: none;
    }
    .css-1djdyxw {
        display: none;
    }
    [data-testid="stFileUploader"] > div > div > div > div > div:nth-child(2) {
        display: none;
    }
    [data-testid="stFileUploader"] > div > div > div > div > div:nth-child(3) {
        display: none;
    }
    [data-testid="stFileUploader"] > div > div > div > div > div:nth-child(4) {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Browse files", type=['jpg', 'jpeg', 'png'], key="image_upload_tool")
    
    if uploaded_file is not None:
        analyze_uploaded_image(uploaded_file)
    
    if st.button("Close", key="close_upload_image"):
        st.session_state.show_upload_image = False
        st.rerun()

if st.session_state.get('show_upload_video', False):
    st.markdown("---")
    st.markdown("### Upload Video")
    
    # Video upload tips
    with st.expander("📝 Tips for Better Video Analysis"):
        st.markdown("""
        **File Limits:**
        • Maximum file size: 50MB (reduced for better stability)
        • Recommended: Under 25MB for faster processing
        • Supported formats: MP4, AVI, MOV, MKV
        
        **Processing time:**
        • Short videos (< 2 min): ~30 seconds
        • Medium videos (2-10 min): ~1-3 minutes  
        • Long videos (> 10 min): ~5-8 minutes
        
        **Best results:**
        • Single person clearly visible
        • Good lighting with clear face visibility
        • Front-facing camera angle
        • Minimal background motion
        """)
    
    uploaded_video = st.file_uploader("Choose video file", type=['mp4', 'avi', 'mov', 'mkv'], key="video_upload_tool")
    
    # Add video compression tips
    st.info("📱 **For Large Videos**: Use live camera or interview mode for real-time analysis without file size limits!")
    
    if uploaded_video is not None:
        # Process the video directly
        # Check daily usage limit
        if not payment_ui.check_daily_limit():
            st.stop()
        
        try:
            # Get video info
            file_size = len(uploaded_video.read())
            uploaded_video.seek(0)  # Reset file pointer
            
            # Check file size limits (reduced for better stability)
            file_size_mb = file_size / (1024 * 1024)
            if file_size > 50 * 1024 * 1024:  # 50MB limit (reduced from 200MB)
                st.error(f"File size ({file_size_mb:.1f}MB) exceeds 50MB limit. Please upload a smaller video.")
                st.info("💡 **Alternative Solutions:**")
                st.markdown("• **Use Live Camera**: Real-time analysis with no file size limits")
                st.markdown("• **Use Interview Mode**: Perfect for screen recording during video calls")
                st.markdown("• **Compress Video**: Use online tools to reduce file size")
                st.markdown("• **Record Shorter Clips**: Break long videos into smaller segments")
                
                # Suggest alternative modes
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎥 Try Live Camera Instead", key="switch_to_live"):
                        st.session_state.show_upload_video = False
                        st.session_state.show_web_camera = True
                        st.rerun()
                with col2:
                    if st.button("🎯 Try Interview Mode Instead", key="switch_to_interview"):
                        st.session_state.show_upload_video = False
                        st.session_state.show_interview_recorder = True
                        st.rerun()
                
                st.stop()
            elif file_size > 25 * 1024 * 1024:  # 25MB warning
                st.warning(f"⚠️ Large video file ({file_size_mb:.1f}MB) detected. Processing may take longer.")
        
        except Exception as e:
            st.error(f"Error reading video file: {str(e)}")
            st.info("💡 **Try these alternatives:**")
            st.markdown("• Use Live Camera mode for real-time analysis")
            st.markdown("• Use Interview Mode for screen recording")
            st.markdown("• Ensure video file is not corrupted")
            st.stop()
        
        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_video.read())
            tmp_video_path = tmp_file.name
        
        # Track usage
        UsageTracker.track_analysis("video", st.session_state.get('user_id'))
        
        try:
            # Display video
            st.video(uploaded_video)
            
            # Create progress placeholder
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress):
                progress_bar.progress(progress)
                status_text.text(f"Processing video... {progress}%")
            
            # Process video with progress tracking
            status_text.text("Analyzing video expressions using AI...")
            video_analyzer = VideoEmotionAnalyzer(significance_threshold=0.1)
            analyses = video_analyzer.process_video(tmp_video_path, max_analyses=10, progress_callback=update_progress)
            video_summary = video_analyzer.get_video_summary()
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if analyses and len(analyses) > 0:
                st.success(f"**Found {len(analyses)} expression moments**")
                
                # Display video summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Analyses", video_summary['total_analyses'])
                    if video_summary['dominant_emotions']:
                        st.markdown("**Dominant Emotions:**")
                        for emotion, count in video_summary['dominant_emotions']:
                            st.write(f"• {emotion}: {count} times")
                
                with col2:
                    st.markdown("**Expression Timeline:**")
                    for moment in video_summary['timeline'][:5]:
                        timestamp = moment['timestamp']
                        minutes = int(timestamp // 60)
                        seconds = int(timestamp % 60)
                        time_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                        st.write(f"{time_str}: {', '.join(moment['expressions'])}")
                
                # Display detailed analyses
                st.markdown("**Detailed Analysis of Significant Moments:**")
                for i, analysis in enumerate(analyses[:8]):
                    timestamp = analysis['timestamp']
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    time_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                    with st.expander(f"Moment {i+1} - {time_str} (Significance: {analysis['significance_score']:.2f})"):
                        st.write(f"**Detected Expressions**: {', '.join(analysis['expressions'])}")
                        st.write(f"**AI Analysis**: {analysis['ai_analysis']}")
                        st.write(f"**Frame**: {analysis['frame_number']}")
                        
                        # Save significant analyses to database only if logged in
                        if st.session_state.get('logged_in', False):
                            save_emotion_analysis(
                                session_id=st.session_state.session_id,
                                expressions=analysis['expressions'],
                                ai_analysis=analysis['ai_analysis'],
                                analysis_type="video",
                                confidence=analysis['significance_score']
                            )
                
                # Show login prompt if not logged in
                if not st.session_state.get('logged_in', False):
                    st.info("💡 Login to save analysis history and access advanced features")
                    if st.button("Login to Save History", key="login_for_video_save_tool"):
                        st.session_state.show_login_modal = True
                        st.rerun()
            
            else:
                st.info("**No facial expressions detected in this video**")
                st.markdown("This could mean:")
                st.markdown("• No clear face visible in the video")
                st.markdown("• Video quality is too low for face detection")
                st.markdown("• Try uploading a video with a clear, well-lit face")
                
        except Exception as e:
            st.error(f"Video analysis error: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_video_path):
                os.unlink(tmp_video_path)
    
    if st.button("Close", key="close_upload_video"):
        st.session_state.show_upload_video = False
        st.rerun()

# Show AI Lie Detector Tool if activated
if st.session_state.get('show_lie_detector_tool', False):
    st.markdown("---")
    st.markdown("### AI Lie Detector Tool")
    
    # Check daily usage limit
    if not PaymentPlans.check_lie_detection_limit():
        st.error("Daily lie detection limit reached (1 per day)")
        st.info("Upgrade to Professional for unlimited lie detections")
        if st.button("Upgrade to Professional", key="upgrade_lie_unlimited"):
            st.switch_page("pages/pricing.py")
    else:
        st.success("AI Lie Detector Active - Upload an image to analyze deception patterns")
        st.info("This tool analyzes micro-expressions and behavioral patterns to assess truthfulness probability (1 use per day)")
        
        # Upload image for lie detection
        lie_uploaded_file = st.file_uploader("Choose image file for lie detection", type=['jpg', 'jpeg', 'png'], key="lie_detector_upload")
        
        if lie_uploaded_file is not None:
            image = cv2.imdecode(np.frombuffer(lie_uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # Process with AI vision
            with st.spinner('Analyzing for deception indicators...'):
                context = st.session_state.get('analysis_context', 'Analyze this person for deception indicators and truthfulness.')
                ai_analysis = ai_vision.analyze_emotion_context(image, [context])
                
                # Run lie detector analysis
                facial_expressions = ai_analysis.get('facial_expressions', [])
                body_patterns = []  # Simple implementation
                
                deception_analysis = lie_detector.analyze_deception(facial_expressions, body_patterns)
                
                # Increment lie detection usage
                PaymentPlans.increment_lie_detection()
                
                deception_probability = deception_analysis.get('deception_probability', 0.0)
                confidence_level = deception_analysis.get('confidence_level', 'Low')
                key_indicators = deception_analysis.get('key_indicators', [])
                
                # Display results
                st.image(image, channels="BGR", caption="Analyzed Image")
                
                # Display deception probability with color coding
                if deception_probability >= 0.7:
                    st.error(f"**Deception Risk**: HIGH ({deception_probability:.1%}) - Confidence: {confidence_level}")
                elif deception_probability >= 0.4:
                    st.warning(f"**Deception Risk**: MEDIUM ({deception_probability:.1%}) - Confidence: {confidence_level}")
                else:
                    st.success(f"**Deception Risk**: LOW ({deception_probability:.1%}) - Confidence: {confidence_level}")
                
                # Display key indicators
                if key_indicators:
                    st.markdown("**Key Deception Indicators:**")
                    for indicator in key_indicators[:5]:
                        st.markdown(f"• {indicator}")
                
                # Get AI interpretation
                ai_interpretation = deception_analysis.get('ai_interpretation', '')
                if ai_interpretation:
                    st.markdown("**AI Deception Analysis:**")
                    st.markdown(ai_interpretation)
        
        # Reset tool state
        if st.button("Close Tool", key="close_lie_detector"):
            st.session_state.show_lie_detector_tool = False
            st.rerun()

# Show Stress Analyzer Tool if activated
if st.session_state.get('show_stress_analyzer_tool', False):
    st.markdown("---")
    st.markdown("### Stress & Anxiety Analyzer Tool")
    
    # Check daily usage limit
    if not PaymentPlans.check_stress_detection_limit():
        st.error("Daily stress analysis limit reached (1 per day)")
        st.info("Upgrade to Professional for unlimited stress analysis")
        if st.button("Upgrade to Professional", key="upgrade_stress_unlimited"):
            st.switch_page("pages/pricing.py")
    else:
        st.success("Stress Analyzer Active - Upload an image to analyze stress and anxiety levels")
        st.info("This tool analyzes facial expressions and body language to assess stress levels (1 use per day)")
        
        # Upload image for stress analysis
        stress_uploaded_file = st.file_uploader("Choose image file for stress analysis", type=['jpg', 'jpeg', 'png'], key="stress_analyzer_upload")
        
        if stress_uploaded_file is not None:
            image = cv2.imdecode(np.frombuffer(stress_uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # Process with stress analyzer
            with st.spinner('Analyzing stress and anxiety levels...'):
                stress_analysis = stress_analyzer.analyze_stress_level(image)
                
                # Increment stress detection usage
                PaymentPlans.increment_stress_detection()
                
                # Display results
                st.image(image, channels="BGR", caption="Analyzed Image")
                
                # Display stress level
                stress_percentage = stress_analysis['stress_percentage']
                stress_level = stress_analysis['stress_level']
                stress_color = stress_analysis['stress_color']
                
                st.markdown(f"**Stress Level**: <span style='color: {stress_color}; font-weight: bold;'>You look {stress_percentage}% stressed ({stress_level})</span>", 
                           unsafe_allow_html=True)
                
                # Show stress indicators
                if stress_analysis.get('indicators'):
                    st.markdown("**Stress Indicators:**")
                    for indicator in stress_analysis['indicators'][:4]:
                        st.markdown(f"• {indicator.replace('_', ' ').title()}")
                
                # Show recommendations
                if stress_analysis.get('recommendations'):
                    st.markdown("**Recommendations:**")
                    for rec in stress_analysis['recommendations'][:3]:
                        st.markdown(f"• {rec}")
        
        # Reset tool state
        if st.button("Close Tool", key="close_stress_analyzer"):
            st.session_state.show_stress_analyzer_tool = False
            st.rerun()

# Show Deception Level Tool if activated
if st.session_state.get('show_deception_level_tool', False):
    st.markdown("---")
    st.markdown("### Deception Level Analyzer")
    
    # Check daily usage limit
    if not PaymentPlans.check_lie_detection_limit():
        st.error("Daily deception analysis limit reached (1 per day)")
        st.info("Upgrade to Professional for unlimited deception analysis")
        if st.button("Upgrade to Professional", key="upgrade_deception_unlimited"):
            st.switch_page("pages/pricing.py")
    else:
        st.success("Deception Level Analyzer Active - Upload an image to analyze deception level")
        st.info("This tool provides precise deception percentage and confidence levels (1 use per day)")
        
        # Upload image for deception level analysis
        deception_uploaded_file = st.file_uploader("Choose image file for deception analysis", type=['jpg', 'jpeg', 'png'], key="deception_level_upload")
        
        if deception_uploaded_file is not None:
            image = cv2.imdecode(np.frombuffer(deception_uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # Process with lie detector
            with st.spinner('Analyzing deception level...'):
                context = st.session_state.get('analysis_context', 'Analyze this person for deception level and truthfulness percentage.')
                ai_analysis = ai_vision.analyze_emotion_context(image, [context])
                
                # Run deception analysis
                facial_expressions = ai_analysis.get('facial_expressions', [])
                body_patterns = []
                
                deception_analysis = lie_detector.analyze_deception(facial_expressions, body_patterns)
                
                # Increment lie detection usage
                PaymentPlans.increment_lie_detection()
                
                # Display results
                st.image(image, channels="BGR", caption="Analyzed Image")
                
                # Calculate deception percentage
                deception_probability = deception_analysis.get('deception_probability', 0.0)
                deception_percentage = int(deception_probability * 100)
                confidence_level = deception_analysis.get('confidence_level', 'Low')
                
                # Display deception level with color coding
                if deception_percentage >= 70:
                    st.error(f"**Deception Level**: {deception_percentage}% (HIGH RISK)")
                elif deception_percentage >= 40:
                    st.warning(f"**Deception Level**: {deception_percentage}% (MEDIUM RISK)")
                else:
                    st.success(f"**Deception Level**: {deception_percentage}% (LOW RISK)")
                
                st.info(f"**Analysis Confidence**: {confidence_level}")
                
                # Show key indicators
                key_indicators = deception_analysis.get('key_indicators', [])
                if key_indicators:
                    st.markdown("**Key Deception Indicators:**")
                    for indicator in key_indicators[:4]:
                        st.markdown(f"• {indicator}")
                
                # AI interpretation
                ai_interpretation = deception_analysis.get('ai_interpretation', '')
                if ai_interpretation:
                    st.markdown("**AI Analysis:**")
                    st.markdown(ai_interpretation)
        
        # Reset tool state
        if st.button("Close Tool", key="close_deception_level"):
            st.session_state.show_deception_level_tool = False
            st.rerun()






# Handle video upload from session state (if set by video tool)
if st.session_state.get('uploaded_video') is not None:
    uploaded_video = st.session_state.uploaded_video
    st.session_state.uploaded_video = None  # Clear it to prevent re-processing
    
    # Check daily usage limit
    if not payment_ui.check_daily_limit():
        st.stop()
    
    # Check file size (limit to 50MB for better stability)
    file_size = len(uploaded_video.getvalue())
    if file_size > 50 * 1024 * 1024:  # 50MB limit (reduced for stability)
        st.error("Video file too large. Please upload a video smaller than 50MB.")
        st.info("💡 **Tips to reduce file size:**")
        st.markdown("• Record at lower resolution (720p instead of 1080p or 4K)")
        st.markdown("• Use shorter video clips (under 3 minutes)")
        st.markdown("• Compress video using online tools before uploading")
        st.markdown("• Try the live camera or interview mode for real-time analysis")
        st.stop()
    
    # Show file size info
    size_mb = file_size / (1024 * 1024)
    st.info(f"📁 Video file size: {size_mb:.1f}MB")
    
    # Save uploaded video to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_video.getvalue())
        tmp_video_path = tmp_file.name
    
    # Track usage
    UsageTracker.track_analysis("video", st.session_state.get('user_id'))
    
    try:
        # Display video
        st.video(uploaded_video)
        
        # Process video with progress bar
        with st.spinner('Analyzing video expressions using AI...'):
            video_analyzer = VideoEmotionAnalyzer(significance_threshold=0.1)
            analyses = video_analyzer.process_video(tmp_video_path, max_analyses=10)
            video_summary = video_analyzer.get_video_summary()
        
        if analyses and len(analyses) > 0:
            st.success(f"**Found {len(analyses)} expression moments**")
            
            # Display video summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Analyses", video_summary['total_analyses'])
                if video_summary['dominant_emotions']:
                    st.markdown("**Dominant Emotions:**")
                    for emotion, count in video_summary['dominant_emotions']:
                        st.write(f"• {emotion}: {count} times")
            
            with col2:
                st.markdown("**Expression Timeline:**")
                for moment in video_summary['timeline'][:5]:
                    timestamp = moment['timestamp']
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    time_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                    st.write(f"{time_str}: {', '.join(moment['expressions'])}")
            
            # Display detailed analyses
            st.markdown("**Detailed Analysis of Significant Moments:**")
            for i, analysis in enumerate(analyses[:8]):  # Show top 8 analyses
                timestamp = analysis['timestamp']
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                time_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                with st.expander(f"Moment {i+1} - {time_str} (Significance: {analysis['significance_score']:.2f})"):
                    st.write(f"**Detected Expressions**: {', '.join(analysis['expressions'])}")
                    st.write(f"**AI Analysis**: {analysis['ai_analysis']}")
                    st.write(f"**Frame**: {analysis['frame_number']}")
                    
                    # Save significant analyses to database only if logged in
                    if st.session_state.get('logged_in', False):
                        save_emotion_analysis(
                            session_id=st.session_state.session_id,
                            expressions=analysis['expressions'],
                            ai_analysis=analysis['ai_analysis'],
                            analysis_type="video",
                            confidence=analysis['significance_score']
                        )
            
            # Show login prompt if not logged in
            if not st.session_state.get('logged_in', False):
                st.info("💡 Login to save analysis history and access advanced features")
                if st.button("Login to Save History", key="login_for_video_save"):
                    st.session_state.show_login_modal = True
                    st.rerun()
        
        else:
            st.info("**No facial expressions detected in this video**")
            st.markdown("This could mean:")
            st.markdown("• No clear face visible in the video")
            st.markdown("• Video quality is too low for face detection")
            st.markdown("• Try uploading a video with a clear, well-lit face")
            
    except Exception as e:
        st.error(f"Video analysis error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_video_path):
            os.unlink(tmp_video_path)



# Screen Recorder Mode
st.markdown("---")
st.markdown("### Live Camera Analysis")
st.markdown("*Real-time emotion analysis using your web camera during video calls*")
st.info("📹 **Web Camera Available**: Live camera analysis works directly in your browser - no installation required!")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Features:**")
    st.markdown("• Works directly in your browser")
    st.markdown("• Real-time camera access")
    st.markdown("• Instant expression analysis")
    st.markdown("• No software installation needed")
    st.markdown("• Perfect for video calls and meetings")

with col2:
    st.markdown("**How to Use:**")
    st.markdown("1. Click 'Start Web Camera' below")
    st.markdown("2. Allow camera access in your browser")
    st.markdown("3. Click 'Analyze Expression' for instant results")
    st.markdown("4. Use during video calls for live feedback")
    st.markdown("5. No downloads or installations required!")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📹 Start Web Camera", type="primary"):
        st.session_state.show_simple_camera = True
        st.rerun()

with col2:
    if st.button("🎯 Interview Mode", type="primary"):
        st.session_state.show_simple_recorder = True
        st.rerun()

with col3:
    if st.button("🧪 Test Debug", type="secondary"):
        st.session_state.show_test_recorder = True
        st.rerun()

# Web Camera Section
if st.session_state.get('show_web_camera', False):
    st.markdown("---")
    st.markdown("### Live Camera Analysis")
    st.markdown("*Real-time emotion analysis using your web camera*")
    
    # Check daily usage limit
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
    else:
        # Live camera streaming
        from live_camera import show_live_camera, init_live_camera
        
        init_live_camera()
        show_live_camera()
        
        # Alternative: Single photo capture
        st.markdown("---")
        st.markdown("#### Alternative: Single Photo Analysis")
        st.markdown("*Take a single photo for instant analysis*")
        
        camera_photo = st.camera_input("Take a photo for expression analysis")
        
        if camera_photo is not None:
            # Check daily usage limit again
            if not check_daily_limit():
                st.error("Daily usage limit reached. Please upgrade to continue.")
            else:
                # Process the camera photo
                try:
                    # Convert uploaded file to image
                    from PIL import Image
                    import numpy as np
                    
                    image = Image.open(camera_photo)
                    image_array = np.array(image)
                    
                    # Analyze with AI Vision
                    ai_vision = AIVisionAnalyzer()
                    
                    with st.spinner('Analyzing your expression...'):
                        analysis = ai_vision.analyze_facial_expressions(image_array)
                    
                    # Track usage
                    UsageTracker.track_analysis("camera", st.session_state.get('user_id'))
                    
                    # Display results
                    st.success("**Photo Analysis Complete!**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.image(image, caption="Analyzed Photo", use_container_width=True)
                    
                    with col2:
                        expressions = analysis.get('facial_expressions', [])
                        if expressions:
                            st.write(f"**Detected Expressions**: {', '.join(expressions)}")
                        
                        emotional_state = analysis.get('emotional_state', 'neutral')
                        st.write(f"**Emotional State**: {emotional_state}")
                        
                        confidence = analysis.get('confidence_level', 'medium')
                        st.write(f"**Confidence Level**: {confidence}")
                    
                    # Show detailed analysis
                    detailed_analysis = analysis.get('detailed_analysis', 'No detailed analysis available')
                    st.write(f"**AI Analysis**: {detailed_analysis}")
                    
                    # Save to database if logged in
                    if st.session_state.get('logged_in', False):
                        save_emotion_analysis(
                            session_id=st.session_state.session_id,
                            expressions=expressions,
                            ai_analysis=detailed_analysis,
                            analysis_type="camera"
                        )
                        st.info("Analysis saved to your history!")
                    else:
                        st.info("Login to save analysis history!")
                        
                except Exception as e:
                    st.error(f"Error processing camera photo: {str(e)}")
        
        # Tips for better camera results
        st.markdown("---")
        st.markdown("#### Tips for Better Results")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Lighting & Position:**")
            st.markdown("• Ensure good lighting on your face")
            st.markdown("• Face the camera directly")
            st.markdown("• Keep camera at eye level")
            st.markdown("• Avoid backlighting")
        
        with col2:
            st.markdown("**During Video Calls:**")
            st.markdown("• Use live analysis for continuous monitoring")
            st.markdown("• Adjust analysis interval based on your needs")
            st.markdown("• Perfect for self-awareness during meetings")
            st.markdown("• Track emotional patterns over time")

# Simple Live Camera Section
if st.session_state.get('show_simple_camera', False):
    st.markdown("---")
    from simple_live_camera import simple_live_camera
    simple_live_camera()

# Simple Screen Recorder Section
if st.session_state.get('show_simple_recorder', False):
    st.markdown("---")
    from simple_screen_recorder import simple_screen_recorder
    simple_screen_recorder()

# Interview Screen Recorder Section (Original)
if st.session_state.get('show_interview_recorder', False):
    st.markdown("---")
    from screen_recorder_interview import show_screen_recorder_interview, init_screen_recorder_interview
    
    init_screen_recorder_interview()
    show_screen_recorder_interview()

# Test Screen Recorder Section
if st.session_state.get('show_test_recorder', False):
    st.markdown("---")
    from test_screen_recorder import test_screen_recorder
    test_screen_recorder()


