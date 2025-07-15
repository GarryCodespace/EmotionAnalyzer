import streamlit as st
import streamlit.components.v1 as components
import base64
import json
import time
from ai_vision_analyzer import AIVisionAnalyzer
from database import save_emotion_analysis
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def show_web_camera():
    """Display web-based camera interface using streamlit-webrtc alternative"""
    
    st.markdown("### Live Camera Analysis")
    st.markdown("*Real-time emotion analysis using your web camera*")
    
    # Check daily usage limit
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    # Instructions
    st.info("📹 **Instructions**: Click 'Start Camera' below, allow camera access, then click 'Analyze Expression' for instant AI analysis!")
    
    # Create camera interface
    camera_html = """
    <div style="text-align: center; margin: 20px 0;">
        <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #ddd; border-radius: 8px; background: #f0f0f0;"></video>
        <br><br>
        <div style="margin: 10px 0;">
            <button id="startBtn" onclick="startCamera()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;">📹 Start Camera</button>
            <button id="captureBtn" onclick="captureFrame()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>🔍 Analyze Expression</button>
            <button id="stopBtn" onclick="stopCamera()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>⏹️ Stop Camera</button>
        </div>
        <div id="status" style="margin: 15px 0; font-weight: bold; color: #666; font-size: 16px;">Click 'Start Camera' to begin</div>
        <canvas id="canvas" width="640" height="480" style="display: none;"></canvas>
    </div>

    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let context = canvas.getContext('2d');
        let stream = null;
        let isAnalyzing = false;
        let captureCount = 0;

        async function startCamera() {
            try {
                const constraints = {
                    video: {
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        facingMode: 'user'
                    }
                };
                
                stream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = stream;
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('captureBtn').disabled = false;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('status').textContent = '✅ Camera ready - Click "Analyze Expression" for AI analysis!';
                document.getElementById('status').style.color = '#28a745';
                
            } catch (err) {
                console.error('Error accessing camera:', err);
                let errorMsg = 'Camera access denied or not available';
                if (err.name === 'NotAllowedError') {
                    errorMsg = 'Camera permission denied. Please allow camera access and try again.';
                } else if (err.name === 'NotFoundError') {
                    errorMsg = 'No camera found. Please connect a camera and try again.';
                }
                document.getElementById('status').textContent = '❌ ' + errorMsg;
                document.getElementById('status').style.color = '#dc3545';
            }
        }

        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('captureBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').textContent = '⏹️ Camera stopped';
            document.getElementById('status').style.color = '#666';
        }

        async function captureFrame() {
            if (isAnalyzing) return;
            
            isAnalyzing = true;
            captureCount++;
            document.getElementById('captureBtn').disabled = true;
            document.getElementById('status').textContent = '🔍 Analyzing expression... Please wait';
            document.getElementById('status').style.color = '#007bff';
            
            try {
                // Draw video frame to canvas
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Convert canvas to base64
                const imageData = canvas.toDataURL('image/jpeg', 0.8);
                
                // Create a hidden form to send data to Streamlit
                const form = document.createElement('form');
                form.method = 'POST';
                form.style.display = 'none';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'camera_frame';
                input.value = imageData;
                
                form.appendChild(input);
                document.body.appendChild(form);
                
                // Trigger Streamlit rerun with the image data
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: {
                        camera_frame: imageData,
                        capture_count: captureCount
                    }
                }, '*');
                
            } catch (err) {
                console.error('Error capturing frame:', err);
                document.getElementById('status').textContent = '❌ Error capturing frame';
                document.getElementById('status').style.color = '#dc3545';
            }
            
            // Re-enable button after 5 seconds
            setTimeout(() => {
                document.getElementById('captureBtn').disabled = false;
                document.getElementById('status').textContent = '✅ Ready for next analysis!';
                document.getElementById('status').style.color = '#28a745';
                isAnalyzing = false;
            }, 5000);
        }

        // Auto-start camera when component loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                if (document.getElementById('startBtn') && !document.getElementById('startBtn').disabled) {
                    startCamera();
                }
            }, 1000);
        });
    </script>
    """
    
    # Display camera component
    camera_data = components.html(camera_html, height=650)
    
    # Handle camera frame data
    if camera_data and 'camera_frame' in str(camera_data):
        process_camera_frame(camera_data)

def show_web_camera():
    """Display web-based camera interface"""
    
    st.markdown("### Live Camera Analysis")
    st.markdown("*Real-time emotion analysis using your web camera*")
    
    # Check daily usage limit
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    # Camera component
    camera_html = create_web_camera_component()
    
    # Create container for the camera
    camera_container = st.container()
    
    with camera_container:
        components.html(camera_html, height=600)
    
    # JavaScript message handler
    message_container = st.empty()
    
    # Handle camera frame data
    if 'camera_frame_data' in st.session_state:
        frame_data = st.session_state.camera_frame_data
        del st.session_state.camera_frame_data
        
        # Process the frame
        process_camera_frame(frame_data)

def process_camera_frame(base64_data):
    """Process captured camera frame"""
    
    try:
        # Decode base64 image
        import base64
        import numpy as np
        from PIL import Image
        import io
        
        # Decode base64 to image
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Analyze with AI Vision
        ai_vision = AIVisionAnalyzer()
        analysis = ai_vision.analyze_facial_expressions(image_array)
        
        # Track usage
        UsageTracker.track_analysis("camera", st.session_state.get('user_id'))
        
        # Display results
        st.success("**Live Analysis Complete!**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Analyzed Frame", use_container_width=True)
        
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
        st.error(f"Error processing camera frame: {str(e)}")

# JavaScript to handle camera messages
camera_js = """
<script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'camera_frame') {
            // Send frame data to Streamlit
            window.parent.postMessage({
                type: 'streamlit_message',
                data: {
                    camera_frame_data: event.data.data
                }
            }, '*');
        }
    });
</script>
"""

def init_camera_handler():
    """Initialize camera message handler"""
    components.html(camera_js, height=0)