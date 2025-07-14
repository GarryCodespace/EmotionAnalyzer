import streamlit as st

st.set_page_config(page_title="Contact - Emoticon", layout="wide")

# Initialize theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Apply theme
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stMarkdown {
        color: #ffffff;
    }
    .stButton > button {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
    }
    .stSelectbox > div > div {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    .stTextArea > div > div > textarea {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)
else:
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
    .stTextArea > div > div > textarea {
        background-color: #f8f8f8;
        color: #000000;
        border: 1px solid #ddd;
    }
    div[data-testid="stAlert"] > div {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
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
    .stMarkdown {
        color: #000000 !important;
    }
    .stText {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo and theme toggle
header_col1, header_col2, header_col3 = st.columns([2, 6, 2])
with header_col1:
    st.markdown("<br><br>", unsafe_allow_html=True)  # Push logo down to align with subtitle
    try:
        st.image("logo.png", width=120)
    except:
        st.markdown("🎭")
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<h1 style='font-size: 3rem; margin: 0; margin-bottom: -35px;'>Contact Us</h1>", unsafe_allow_html=True)
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<p style='margin-top: -35px;'>Get in Touch with the Emoticon Team</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    theme_button_text = "🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"
    if st.button(theme_button_text, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    if st.button("ℹ️ About", key="about_button"):
        st.switch_page("pages/about.py")

st.markdown("---")

# Contact form and information
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## Send us a Message")
    
    # Contact form
    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Name *", placeholder="Your full name")
        email = st.text_input("Email *", placeholder="your.email@example.com")
        subject = st.selectbox("Subject *", [
            "General Inquiry",
            "Technical Support",
            "Bug Report",
            "Feature Request",
            "Partnership Opportunity",
            "Press Inquiry",
            "Other"
        ])
        message = st.text_area("Message *", placeholder="Tell us how we can help you...", height=150)
        
        submitted = st.form_submit_button("Send Message")
        
        if submitted:
            if name and email and message:
                st.success("Thank you for your message! We'll get back to you within 24 hours.")
                # Here you would normally send the email or save to database
            else:
                st.error("Please fill in all required fields marked with *")

with col2:
    st.markdown("## Get in Touch")
    
    st.markdown("""
    ### Direct Contact
    
    📧 **Email**: support@emoticon.ai
    
    📱 **Phone**: +1 (555) 123-4567
    
    🕐 **Hours**: Monday - Friday, 9 AM - 6 PM PST
    
    ---
    
    ### FOLLOW US
    
    📸 **INSTAGRAM**: [@EMOTICON.AI](https://www.instagram.com/emoticon.ai)
    
    🐦 **TWITTER**: [@EMOTICONAI](https://twitter.com/emoticon)
    
    💼 **LINKEDIN**: [EMOTICON](https://linkedin.com/company/emoticon)
    
    🐙 **GITHUB**: [GITHUB.COM/EMOTICON](https://github.com/emoticon)
    
    ---
    
    ### Office Location
    
    📍 **Address**:
    
    Emoticon AI Inc.
    
    123 Innovation Drive
    
    San Francisco, CA 94105
    
    United States
    """)

st.markdown("---")

# FAQ Section
st.markdown("## Frequently Asked Questions")

with st.expander("How accurate is the emotion detection?"):
    st.markdown("""
    Our emotion detection system uses advanced computer vision with MediaPipe for facial landmark detection 
    and OpenAI's GPT-4o for psychological analysis. The accuracy depends on lighting conditions, camera quality, 
    and facial visibility, but typically achieves 85-90% accuracy for basic emotions.
    """)

with st.expander("Is my data secure and private?"):
    st.markdown("""
    Yes, we take privacy seriously. Video processing happens locally on your device, and only anonymized 
    analysis results are stored. We never store or transmit your actual video footage. All data is encrypted 
    and follows industry-standard security practices.
    """)

with st.expander("What devices and browsers are supported?"):
    st.markdown("""
    Emoticon works on most modern web browsers including Chrome, Firefox, Safari, and Edge. 
    You'll need a working webcam and microphone permissions. The app is optimized for desktop 
    and laptop computers with good lighting conditions.
    """)

with st.expander("Can I use this for commercial purposes?"):
    st.markdown("""
    Please contact us for commercial licensing options. We offer enterprise solutions for 
    businesses, researchers, and developers who want to integrate emotion analysis into 
    their products or services.
    """)

with st.expander("How do I report a bug or suggest a feature?"):
    st.markdown("""
    You can report bugs or suggest features by:
    1. Using the contact form above with "Bug Report" or "Feature Request" as the subject
    2. Emailing us directly at support@emoticon.ai
    3. Opening an issue on our GitHub repository
    """)

# Navigation
st.markdown("---")
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    if st.button("← Back to Main App"):
        st.switch_page("app.py")
with nav_col2:
    if st.button("About Emoticon →"):
        st.switch_page("pages/about.py")