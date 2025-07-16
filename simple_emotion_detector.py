import streamlit as st
import cv2
import numpy as np
import time
from ai_vision_analyzer import AIVisionAnalyzer
from database import save_emotion_analysis
from datetime import datetime
import base64
from PIL import Image
import io

class SimpleEmotionDetector:
    def __init__(self):
        self.ai_vision = AIVisionAnalyzer()
        self.last_emotion = None
        self.last_analysis_time = 0
        self.analysis_cooldown = 3  # 3 seconds between analyses
        
    def detect_emotion_change(self, frame):
        """Simple emotion detection that takes photos when new emotions are detected"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_analysis_time < self.analysis_cooldown:
            return None
            
        try:
            # Analyze current frame
            analysis = self.ai_vision.analyze_facial_expressions(frame)
            
            if analysis and 'emotional_state' in analysis:
                current_emotion = analysis['emotional_state']
                
                # Check if emotion has changed
                if current_emotion != self.last_emotion:
                    self.last_emotion = current_emotion
                    self.last_analysis_time = current_time
                    
                    # Return the analysis for this new emotion
                    return {
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'emotion': current_emotion,
                        'analysis': analysis.get('detailed_analysis', 'No detailed analysis available'),
                        'confidence': analysis.get('confidence_level', 'medium'),
                        'expressions': analysis.get('facial_expressions', [])
                    }
                    
        except Exception as e:
            st.error(f"Error analyzing emotion: {str(e)}")
            
        return None
        
    def reset(self):
        """Reset detector state"""
        self.last_emotion = None
        self.last_analysis_time = 0

def simple_emotion_detector():
    """Simple emotion detector that takes photos when new emotions are detected"""
    st.markdown("### 📸 Simple Emotion Detector")
    st.markdown("*Takes a photo every time a new emotion is detected and sends to ChatGPT for analysis*")
    
    # Initialize detector
    if 'emotion_detector' not in st.session_state:
        st.session_state.emotion_detector = SimpleEmotionDetector()
    
    # Initialize emotion history
    if 'emotion_history' not in st.session_state:
        st.session_state.emotion_history = []
    
    # Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📹 Start Detection", type="primary"):
            st.session_state.detection_active = True
            st.session_state.emotion_detector.reset()
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Detection"):
            st.session_state.detection_active = False
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.emotion_history = []
            st.rerun()
    
    # Show current status
    if st.session_state.get('detection_active', False):
        st.success("🟢 Detection Active - Looking for emotion changes...")
        
        # Video capture
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Cannot access camera. Please check camera permissions.")
            return
        
        # Create containers for live feed and results
        video_container = st.empty()
        results_container = st.empty()
        
        # Real-time detection loop
        frame_count = 0
        max_frames = 1000  # Limit to prevent infinite loop
        
        while st.session_state.get('detection_active', False) and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Failed to capture frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Display live video
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_container.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Check for emotion changes every 30 frames (about 1 second)
            if frame_count % 30 == 0:
                emotion_result = st.session_state.emotion_detector.detect_emotion_change(frame)
                
                if emotion_result:
                    # New emotion detected!
                    st.session_state.emotion_history.append(emotion_result)
                    
                    # Save to database if logged in
                    if st.session_state.get('logged_in', False):
                        save_emotion_analysis(
                            session_id=st.session_state.get('session_id', 'anonymous'),
                            expressions=emotion_result['expressions'],
                            ai_analysis=emotion_result['analysis'],
                            analysis_type="simple_live"
                        )
                    
                    # Show notification
                    st.success(f"📸 New emotion detected: {emotion_result['emotion']}")
                    
                    # Play notification sound (if supported)
                    st.balloons()
            
            frame_count += 1
            time.sleep(0.1)  # Small delay to prevent overwhelming the system
        
        cap.release()
    
    else:
        st.info("👆 Click 'Start Detection' to begin monitoring for emotion changes")
    
    # Display emotion history
    if st.session_state.get('emotion_history'):
        st.markdown("---")
        st.markdown("### 📊 Detected Emotions")
        
        # Show recent emotions
        recent_emotions = st.session_state.emotion_history[-10:]  # Last 10 emotions
        
        for i, result in enumerate(reversed(recent_emotions)):
            with st.expander(f"🎭 {result['emotion']} at {result['timestamp']}", expanded=i==0):
                st.markdown(f"**Confidence:** {result['confidence']}")
                
                if result['expressions']:
                    st.markdown(f"**Expressions:** {', '.join(result['expressions'])}")
                
                st.markdown("**AI Analysis:**")
                st.markdown(result['analysis'])
        
        # Show emotion timeline
        if len(st.session_state.emotion_history) > 1:
            st.markdown("### 📈 Emotion Timeline")
            emotions = [r['emotion'] for r in st.session_state.emotion_history]
            timestamps = [r['timestamp'] for r in st.session_state.emotion_history]
            
            timeline_text = " → ".join([f"{t}: {e}" for t, e in zip(timestamps, emotions)])
            st.text(timeline_text)
    
    # Instructions
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Click 'Start Detection'** to begin monitoring
    2. **Move naturally** in front of the camera
    3. **When your emotion changes**, the system automatically takes a photo
    4. **ChatGPT analyzes** the new emotion and provides insights
    5. **View your emotion history** below the video feed
    """)
    
    st.markdown("### 🎯 Tips for Best Results")
    st.markdown("""
    - **Good lighting** helps emotion detection
    - **Face the camera** directly
    - **Natural expressions** work best
    - **Wait 3 seconds** between emotion changes for analysis
    - **Try different emotions** to test the system
    """)

if __name__ == "__main__":
    simple_emotion_detector()