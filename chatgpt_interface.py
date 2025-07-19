import streamlit as st
import cv2
import numpy as np
from ai_vision_analyzer import AIVisionAnalyzer
from datetime import datetime
import base64
from PIL import Image
import io

def create_chatgpt_interface():
    """Create a ChatGPT-style interface for emotion analysis"""
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize AI analyzer
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIVisionAnalyzer()
    
    # Chat-style header
    st.markdown("""
    <div style="text-align: center; padding: 20px; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.5rem; color: #333;">🎭 Emoticon AI</h1>
        <p style="margin: 10px 0; color: #666; font-size: 1.1rem;">Analyze emotions in images, videos, or live camera</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                    <div style="background-color: #007bff; color: white; padding: 12px 16px; border-radius: 18px; max-width: 70%; margin-left: 20%;">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show uploaded image if present
                if 'image' in message:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(message['image'], caption="Uploaded Image", use_container_width=True)
            
            elif message['role'] == 'assistant':
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div style="background-color: #f1f3f4; color: #333; padding: 12px 16px; border-radius: 18px; max-width: 70%; margin-right: 20%;">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area at bottom
    st.markdown("---")
    
    # Create columns for different input types
    input_col1, input_col2, input_col3, input_col4 = st.columns([2, 1, 1, 1])
    
    with input_col1:
        user_input = st.text_input("Ask about emotions or upload content...", 
                                  placeholder="e.g., 'Analyze my emotion', 'How do I look?', 'Am I stressed?'",
                                  key="chat_input")
    
    with input_col2:
        uploaded_image = st.file_uploader("📷 Image", type=['jpg', 'jpeg', 'png'], 
                                        key="chat_image_upload", label_visibility="collapsed")
    
    with input_col3:
        uploaded_video = st.file_uploader("🎥 Video", type=['mp4', 'avi', 'mov'], 
                                        key="chat_video_upload", label_visibility="collapsed")
    
    with input_col4:
        if st.button("📹 Live Cam", use_container_width=True):
            st.session_state.show_chat_camera = True
            st.rerun()
    
    # Process user input
    if user_input or uploaded_image or uploaded_video:
        # Add user message to chat
        if user_input:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
        
        # Process uploaded content
        if uploaded_image:
            # Add image to chat
            image = Image.open(uploaded_image)
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "I uploaded an image for emotion analysis",
                'image': image,
                'timestamp': datetime.now()
            })
            
            # Analyze image
            image_array = np.array(image)
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            with st.spinner('Analyzing your emotion...'):
                analysis = st.session_state.ai_analyzer.analyze_facial_expressions(image_array)
            
            # Format response
            if analysis:
                response = format_emotion_response(analysis)
            else:
                response = "I couldn't detect clear facial expressions in this image. Try with better lighting or a clearer face view."
            
            # Add AI response to chat
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
        
        elif uploaded_video:
            # Add video message to chat
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "I uploaded a video for emotion analysis",
                'timestamp': datetime.now()
            })
            
            # Add processing message
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': "📹 Video analysis is being processed... This may take a few moments for longer videos.",
                'timestamp': datetime.now()
            })
        
        elif user_input:
            # Simple text response
            response = generate_text_response(user_input.lower())
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
        
        # Clear input and rerun
        st.rerun()
    
    # Live camera section
    if st.session_state.get('show_chat_camera', False):
        st.markdown("---")
        st.markdown("### 📹 Live Camera Analysis")
        
        # Camera controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📸 Capture & Analyze", type="primary"):
                # This would trigger camera capture and analysis
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': "📸 Live camera analysis coming soon! Use the image upload for now.",
                    'timestamp': datetime.now()
                })
                st.rerun()
        
        with col2:
            if st.button("❌ Close Camera"):
                st.session_state.show_chat_camera = False
                st.rerun()

def format_emotion_response(analysis):
    """Format AI analysis into a chat-friendly response"""
    if not analysis:
        return "I couldn't analyze the emotions in this image."
    
    response_parts = []
    
    # Main emotion
    if 'emotional_state' in analysis:
        response_parts.append(f"**Your main emotion**: {analysis['emotional_state']}")
    
    # Confidence
    if 'confidence_level' in analysis:
        response_parts.append(f"**Confidence**: {analysis['confidence_level']}")
    
    # Detailed analysis
    if 'detailed_analysis' in analysis:
        response_parts.append(f"**Analysis**: {analysis['detailed_analysis']}")
    
    # Expressions detected
    if 'facial_expressions' in analysis and analysis['facial_expressions']:
        expressions = ', '.join(analysis['facial_expressions'])
        response_parts.append(f"**Expressions detected**: {expressions}")
    
    return '\n\n'.join(response_parts) if response_parts else "Analysis complete, but no specific emotions were detected."

def generate_text_response(user_input):
    """Generate contextual responses to text input"""
    responses = {
        'hello': "Hi! I'm Emoticon AI. Upload an image or video, and I'll analyze the emotions for you! 😊",
        'hi': "Hello! Ready to analyze some emotions? Upload an image or use the live camera!",
        'help': "I can analyze emotions in:\n• 📷 **Images** - Upload any photo\n• 🎥 **Videos** - Upload video files\n• 📹 **Live Camera** - Real-time analysis\n\nJust upload content or ask me questions!",
        'how': "I use advanced AI to detect facial expressions and body language, then provide psychological insights about emotions, stress levels, and authenticity.",
        'what': "I'm an AI emotion analyzer that can detect happiness, sadness, anger, surprise, fear, and more complex emotional states from visual content.",
        'stressed': "Upload a photo and I'll analyze your stress levels! I can detect tension in facial muscles, body posture, and micro-expressions.",
        'happy': "That's great! Upload a photo and I'll confirm how happy you look and provide insights about your expression.",
        'sad': "I can help analyze your emotional state. Upload an image and I'll provide supportive insights about what I detect.",
        'lie': "I can detect deception indicators through micro-expressions and body language analysis. Upload an image for lie detection analysis!",
        'angry': "Upload a photo and I'll analyze anger levels and provide insights about emotional intensity and possible triggers.",
    }
    
    # Check for keywords in user input
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # Default response
    return "I'm here to analyze emotions! Try uploading an image, video, or asking questions like:\n• 'How do I look?'\n• 'Am I stressed?'\n• 'Analyze my emotion'\n• 'Help with lie detection'"

if __name__ == "__main__":
    create_chatgpt_interface()