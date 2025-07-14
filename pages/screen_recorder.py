import streamlit as st
import cv2
import numpy as np
import time
import uuid
from datetime import datetime
import os
from openai_analyzer import analyze_expression
from video_analyzer import VideoEmotionAnalyzer
from database import save_emotion_analysis

def main():
    st.set_page_config(page_title="Emoticon - Screen Recorder", layout="wide")
    
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
            <a href="/" class="nav-item">Home</a>
            <a href="/about" class="nav-item">About</a>
            <a href="/contact" class="nav-item">Contact</a>
            <a href="/screen_recorder" class="nav-item active">Screen Recorder</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


    
    # Header with logo
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image("logo.png", width=60)
        except:
            st.write("🎬")
    with col2:
        st.title("Screen Recorder Mode")
        st.write("Record and analyze expressions during video calls")
    
    # Initialize session state
    if 'recorder_session_id' not in st.session_state:
        st.session_state.recorder_session_id = str(uuid.uuid4())
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = VideoEmotionAnalyzer(significance_threshold=0.2)
    if 'last_analysis_time' not in st.session_state:
        st.session_state.last_analysis_time = 0
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    
    # Instructions
    st.markdown("### 🎯 How to Use Screen Recorder Mode")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**For External Video Calls:**")
        st.markdown("1. Open your video call app (Zoom, Teams, etc.)")
        st.markdown("2. Position this window where you can see it")
        st.markdown("3. Use the webcam mode below during your call")
        st.markdown("4. Get live analysis as you speak")
    
    with col2:
        st.markdown("**Features:**")
        st.markdown("• Real-time expression analysis")
        st.markdown("• Smart detection of significant changes")
        st.markdown("• Configurable sensitivity")
        st.markdown("• Session history tracking")
        st.markdown("• Export analysis results")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sensitivity = st.slider(
            "Analysis Sensitivity",
            min_value=0.1,
            max_value=0.5,
            value=0.2,
            step=0.05,
            help="Lower values = more sensitive to changes"
        )
        st.session_state.analyzer.significance_threshold = sensitivity
    
    with col2:
        cooldown = st.slider(
            "Analysis Cooldown (seconds)",
            min_value=3,
            max_value=15,
            value=8,
            help="Minimum time between analyses"
        )
    
    with col3:
        auto_save = st.checkbox("Auto-save significant moments", value=True)
    
    # Live Analysis Section
    st.markdown("### 📹 Live Analysis")
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎥 Start Live Analysis", type="primary"):
            st.session_state.is_recording = True
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Analysis"):
            st.session_state.is_recording = False
            st.rerun()
    
    with col3:
        if st.button("🔄 Clear Results"):
            st.session_state.analysis_results = []
            st.rerun()
    
    # Live camera feed and analysis
    if st.session_state.is_recording:
        st.markdown("**🔴 Live Analysis Active**")
        
        # Webcam capture with streamlit-webrtc or basic opencv
        camera_placeholder = st.empty()
        analysis_placeholder = st.empty()
        
        # Simple webcam capture
        camera = cv2.VideoCapture(0)
        
        if camera.isOpened():
            # Take a frame for analysis
            ret, frame = camera.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display frame
                camera_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Analyze frame
                current_time = time.time()
                if current_time - st.session_state.last_analysis_time > cooldown:
                    result = st.session_state.analyzer.analyze_video_frame(frame_rgb, current_time)
                    
                    if result:
                        st.session_state.last_analysis_time = current_time
                        result_data = {
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'expressions': result.get('expressions', []),
                            'ai_analysis': result.get('ai_analysis', ''),
                            'significance': result.get('significance_score', 0.0)
                        }
                        st.session_state.analysis_results.append(result_data)
                        
                        # Show latest analysis
                        with analysis_placeholder.container():
                            st.success("🎯 **New Analysis Detected!**")
                            st.write(f"**Expressions:** {', '.join(result_data['expressions'])}")
                            st.write(f"**Analysis:** {result_data['ai_analysis']}")
                            st.write(f"**Significance:** {result_data['significance']:.2f}")
                        
                        # Save to database if enabled
                        if auto_save:
                            save_emotion_analysis(
                                st.session_state.recorder_session_id,
                                result.get('expressions', []),
                                result.get('ai_analysis', ''),
                                'screen_recording',
                                result.get('significance_score', 0.0)
                            )
                
                # Auto-refresh for continuous recording
                time.sleep(2)
                st.rerun()
            
            camera.release()
        else:
            st.error("Camera not available. Please check your camera permissions.")
            st.session_state.is_recording = False
    
    # Analysis Results
    st.markdown("### 📊 Analysis Results")
    
    if st.session_state.analysis_results:
        # Recent results
        st.markdown("**Recent Analyses:**")
        for i, result in enumerate(reversed(st.session_state.analysis_results[-10:])):
            with st.expander(f"🕐 {result['timestamp']} - Significance: {result['significance']:.2f}"):
                st.write(f"**Expressions:** {', '.join(result['expressions'])}")
                st.write(f"**Analysis:** {result['ai_analysis']}")
        
        # Summary statistics
        st.markdown("**📈 Session Summary:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Analyses", len(st.session_state.analysis_results))
        
        with col2:
            if st.session_state.analysis_results:
                avg_significance = sum(r['significance'] for r in st.session_state.analysis_results) / len(st.session_state.analysis_results)
                st.metric("Average Significance", f"{avg_significance:.2f}")
        
        with col3:
            # Most common expressions
            all_expressions = []
            for result in st.session_state.analysis_results:
                all_expressions.extend(result['expressions'])
            
            if all_expressions:
                from collections import Counter
                most_common = Counter(all_expressions).most_common(1)[0]
                st.metric("Most Common Expression", most_common[0])
        
        # Export results
        if st.button("📥 Export Session Data"):
            import json
            session_data = {
                'session_id': st.session_state.recorder_session_id,
                'timestamp': datetime.now().isoformat(),
                'results': st.session_state.analysis_results
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(session_data, indent=2),
                file_name=f"emotion_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("No analysis results yet. Start live analysis to see results here.")
    
    # Tips and guidance
    st.markdown("### 💡 Tips for Best Results")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Lighting:**")
        st.markdown("• Ensure good lighting on your face")
        st.markdown("• Avoid backlighting")
        st.markdown("• Keep camera at eye level")
    
    with col2:
        st.markdown("**During Video Calls:**")
        st.markdown("• Keep this window visible")
        st.markdown("• Position camera for clear face view")
        st.markdown("• Minimize background movement")

if __name__ == "__main__":
    main()