import streamlit as st

st.set_page_config(page_title="About Emoticon", layout="wide")

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
        <span class="nav-item">Home</span>
        <span class="nav-item active">About</span>
        <span class="nav-item">Contact</span>
        <span class="nav-item">Screen Recorder</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation functionality using columns - styled buttons
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 2])

with nav_col1:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")

with nav_col2:
    if st.button("About", key="nav_about", use_container_width=True):
        st.switch_page("pages/about.py")

with nav_col3:
    if st.button("Contact", key="nav_contact", use_container_width=True):
        st.switch_page("pages/contact.py")

with nav_col4:
    if st.button("Screen Recorder", key="nav_screen", use_container_width=True):
        st.switch_page("pages/screen_recorder.py")

# Style the navigation buttons to match the design
st.markdown("""
<style>
/* Style navigation buttons */
[data-testid="stColumns"] [data-testid="stButton"] > button {
    background-color: #1f1f1f;
    border: none;
    color: #ffffff;
    font-size: 16px;
    font-weight: 500;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
}

/* Active state for about button */
[data-testid="stColumns"] [data-testid="stButton"]:nth-child(2) > button {
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
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<h1 style='font-size: 3rem; margin: 0; margin-bottom: -35px;'>About Emoticon</h1>", unsafe_allow_html=True)
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<p style='margin-top: -35px;'>Understanding the Technology Behind Emotion Detection</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    theme_button_text = "🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"
    if st.button(theme_button_text, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("---")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    ## Why Emoticon?
    
    Human expressions are often missed — fleeting moments of truth hidden in plain sight. Inspired by criminal interrogation techniques, **Emoticon** recognizes over 40 facial gestures, combining computer vision and AI to interpret what your face says before your mouth speaks.
    
    ## Features
    
    • **Real-time face gesture tracking** using webcam
    
    • **40+ micro-expressions** (eyebrows, lips, head movement, etc.)
    
    • **GPT-powered emotional insight engine**
    
    • **Built with Streamlit + MediaPipe + OpenAI + React**
    """)

with col2:
    st.markdown("""
    ## How It Works
    
    You look at the camera. Our model sees facial landmarks. Expressions are matched. Emotional context is inferred. Insight is shown instantly.
    
    ## What's Next
    
    Emoticon will grow into a fully-fledged emotional analytics platform — empowering researchers, UX designers, and humans who want to understand other humans better.
    
    ## Technical Implementation
    
    - **Computer Vision**: MediaPipe Face Mesh for 468 facial landmarks
    - **Expression Detection**: 100+ predefined gestures using geometric analysis
    - **AI Analysis**: OpenAI GPT-4o for psychological insights
    - **Database**: PostgreSQL for storing analysis results and user sessions
    """)

st.markdown("---")

# Additional technical details
st.markdown("""
## Key Technologies

### MediaPipe Face Mesh
Advanced facial landmark detection that identifies 468 3D points on the human face in real-time, enabling precise gesture recognition.

### OpenAI GPT-4o Integration
Cutting-edge language model that provides psychological insights and emotional interpretation based on detected facial expressions.

### Real-time Processing Pipeline
Optimized video processing system that analyzes facial expressions continuously while maintaining high performance.

### Smart Expression Detection
Intelligent system that recognizes significant expression changes to provide meaningful analysis without overwhelming the user.
""")

# Navigation
st.markdown("---")
if st.button("← Back to Main App"):
    st.switch_page("app.py")