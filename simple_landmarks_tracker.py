import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
import time
from openai_analyzer import OpenAIAnalyzer

class SimpleLandmarksTracker:
    """
    Simple facial landmarks tracker inspired by https://github.com/agusrajuthaliyan/Facial-Landmarks-Tracker.git
    Optimized for performance and real-time emotion detection
    """
    
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize face mesh with optimized settings for performance
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,  # Single face for better performance
            refine_landmarks=False,  # Disable refinement for speed
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Initialize OpenAI analyzer
        self.openai_analyzer = OpenAIAnalyzer()
        
        # Key facial landmarks for emotion detection
        self.key_landmarks = {
            'left_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            'right_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            'mouth': [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 78],
            'eyebrows': [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
            'nose': [1, 2, 5, 4, 6, 168, 8, 9, 10, 151]
        }
        
        # Emotion tracking
        self.last_emotion = None
        self.last_analysis_time = 0
        self.analysis_interval = 2.0  # Analyze every 2 seconds
        
    def detect_landmarks(self, frame):
        """Detect facial landmarks in frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]  # Return first face
        return None
    
    def draw_landmarks(self, frame, landmarks):
        """Draw key landmarks on frame with different colors for different features"""
        if not landmarks:
            return frame
        
        h, w, _ = frame.shape
        
        # Define colors for different facial features
        colors = {
            'left_eye': (0, 255, 0),    # Green
            'right_eye': (0, 255, 0),   # Green  
            'mouth': (0, 0, 255),       # Red
            'eyebrows': (255, 0, 0),    # Blue
            'nose': (255, 255, 0)       # Cyan
        }
        
        # Draw landmarks for each feature
        for feature, indices in self.key_landmarks.items():
            color = colors[feature]
            for idx in indices:
                if idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 2, color, -1)
        
        return frame
    
    def analyze_emotion_change(self, frame):
        """Analyze if emotion has changed significantly"""
        current_time = time.time()
        
        # Check if enough time has passed since last analysis
        if current_time - self.last_analysis_time < self.analysis_interval:
            return None
        
        try:
            # Use OpenAI to analyze the current frame
            analysis = self.openai_analyzer.analyze_image(frame)
            
            if analysis and 'emotion' in analysis:
                current_emotion = analysis['emotion']
                
                # Check if emotion has changed
                if current_emotion != self.last_emotion:
                    self.last_emotion = current_emotion
                    self.last_analysis_time = current_time
                    
                    return {
                        'emotion': current_emotion,
                        'confidence': analysis.get('confidence', 0.8),
                        'analysis': analysis.get('detailed_analysis', ''),
                        'timestamp': time.strftime('%H:%M:%S')
                    }
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
        
        return None
    
    def run_tracker(self):
        """Run the landmarks tracker with real-time emotion detection"""
        st.markdown("### 🎯 Simple Landmarks Tracker")
        st.markdown("*Real-time facial landmark detection with emotion analysis*")
        
        # Initialize session state
        if 'tracker_running' not in st.session_state:
            st.session_state.tracker_running = False
        if 'emotion_detections' not in st.session_state:
            st.session_state.emotion_detections = []
        
        # Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Tracker", type="primary"):
                st.session_state.tracker_running = True
                st.rerun()
        
        with col2:
            if st.button("⏹️ Stop Tracker"):
                st.session_state.tracker_running = False
                st.rerun()
        
        with col3:
            if st.button("🗑️ Clear History"):
                st.session_state.emotion_detections = []
                st.rerun()
        
        # Real-time tracking
        if st.session_state.tracker_running:
            st.success("🟢 Tracker Active - Detecting landmarks and emotions...")
            
            # Create placeholders for video and results
            video_placeholder = st.empty()
            info_placeholder = st.empty()
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Cannot access camera")
                return
            
            frame_count = 0
            max_frames = 500  # Limit frames to prevent infinite loop
            
            try:
                while st.session_state.tracker_running and frame_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Flip frame for mirror effect
                    frame = cv2.flip(frame, 1)
                    
                    # Detect landmarks
                    landmarks = self.detect_landmarks(frame)
                    
                    # Draw landmarks on frame
                    if landmarks:
                        frame = self.draw_landmarks(frame, landmarks)
                        
                        # Check for emotion changes every 30 frames
                        if frame_count % 30 == 0:
                            emotion_result = self.analyze_emotion_change(frame)
                            
                            if emotion_result:
                                st.session_state.emotion_detections.append(emotion_result)
                                
                                # Show notification
                                info_placeholder.success(f"🎭 New emotion detected: {emotion_result['emotion']} ({emotion_result['confidence']:.0%} confidence)")
                    
                    # Display frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                    
                    frame_count += 1
                    time.sleep(0.1)  # Control frame rate
                
            finally:
                cap.release()
        
        else:
            st.info("👆 Click 'Start Tracker' to begin landmark detection and emotion analysis")
        
        # Show emotion history
        if st.session_state.emotion_detections:
            st.markdown("---")
            st.markdown("### 📊 Emotion Detection History")
            
            # Show recent detections
            recent_detections = st.session_state.emotion_detections[-5:]  # Last 5
            
            for detection in reversed(recent_detections):
                with st.expander(f"🎭 {detection['emotion']} at {detection['timestamp']}", expanded=False):
                    st.markdown(f"**Confidence:** {detection['confidence']:.0%}")
                    if detection['analysis']:
                        st.markdown(f"**Analysis:** {detection['analysis']}")
        
        # Performance tips
        st.markdown("---")
        st.markdown("### 💡 Performance Tips")
        st.markdown("""
        - **Good lighting** improves landmark detection accuracy
        - **Face the camera** directly for best results  
        - **Stable position** helps with consistent tracking
        - **Clear facial expressions** work better for emotion detection
        - **Minimal background movement** improves performance
        """)

def simple_landmarks_tracker():
    """Main function to run the simple landmarks tracker"""
    tracker = SimpleLandmarksTracker()
    tracker.run_tracker()

if __name__ == "__main__":
    simple_landmarks_tracker()