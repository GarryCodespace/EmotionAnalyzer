import streamlit as st
import streamlit.components.v1 as components
import time
import base64
from PIL import Image
import io
import numpy as np
from ai_vision_analyzer import AIVisionAnalyzer
from openai_analyzer import analyze_expression
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def simple_screen_recorder():
    """Simple screen recorder that works reliably"""
    
    st.markdown("### Screen Recording for Interviews")
    st.markdown("*Simple and reliable screen recording with emotion analysis*")
    
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    # Simple instructions
    st.info("📹 **How to use**: Click 'Start Recording' → Allow screen sharing → Click 'Capture & Analyze' for analysis")
    
    # Simple HTML that just captures screen
    html_code = """
    <div style="text-align: center; margin: 20px;">
        <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #ddd; border-radius: 8px;"></video>
        <br><br>
        <button id="startBtn" onclick="startRecording()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;">
            Start Recording
        </button>
        <button id="captureBtn" onclick="captureFrame()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
            Capture & Analyze
        </button>
        <button id="stopBtn" onclick="stopRecording()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
            Stop
        </button>
        <div id="status" style="margin-top: 15px; font-size: 16px; color: #666;">Click 'Start Recording' to begin</div>
        <canvas id="canvas" width="640" height="480" style="display: none;"></canvas>
    </div>
    
    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let ctx = canvas.getContext('2d');
        let stream = null;
        let frameCount = 0;
        
        async function startRecording() {
            try {
                stream = await navigator.mediaDevices.getDisplayMedia({
                    video: { width: 640, height: 480 },
                    audio: false
                });
                
                video.srcObject = stream;
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('captureBtn').disabled = false;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('status').textContent = '✅ Recording started - Click "Capture & Analyze" to analyze current frame';
                document.getElementById('status').style.color = '#28a745';
                
                stream.getVideoTracks()[0].addEventListener('ended', stopRecording);
                
            } catch (err) {
                console.error('Error:', err);
                document.getElementById('status').textContent = '❌ Screen sharing failed - Please allow screen access';
                document.getElementById('status').style.color = '#dc3545';
            }
        }
        
        function captureFrame() {
            if (!stream) return;
            
            frameCount++;
            document.getElementById('status').textContent = `📸 Capturing frame ${frameCount}...`;
            document.getElementById('status').style.color = '#007bff';
            
            // Draw video frame to canvas
            ctx.drawImage(video, 0, 0, 640, 480);
            
            // Convert to base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {
                    action: 'analyze_frame',
                    frame_data: imageData,
                    frame_count: frameCount,
                    timestamp: Date.now()
                }
            }, '*');
            
            document.getElementById('status').textContent = `🔍 Analyzing frame ${frameCount}...`;
        }
        
        function stopRecording() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('captureBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').textContent = '⏹️ Recording stopped';
            document.getElementById('status').style.color = '#666';
        }
        
        // Listen for results
        window.addEventListener('message', function(event) {
            if (event.data.type === 'analysis_complete') {
                const result = event.data.data;
                document.getElementById('status').textContent = `✅ Analysis complete - Frame ${result.frame_count}`;
                document.getElementById('status').style.color = '#28a745';
            }
        });
    </script>
    """
    
    # Display component
    component_value = components.html(html_code, height=650)
    
    # Process captured frame
    if component_value and isinstance(component_value, dict) and component_value.get('action') == 'analyze_frame':
        with st.spinner('Analyzing captured frame...'):
            result = analyze_captured_frame(component_value)
            
            if result:
                # Display results
                st.success(f"✅ Frame {result['frame_count']} Analysis Complete")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Emotional State", result['emotion'])
                    st.metric("Expressions", result['expressions'])
                with col2:
                    st.metric("Confidence", result['confidence'])
                    st.metric("Frame Count", result['frame_count'])
                
                # Show detailed analysis
                st.markdown("### Detailed Analysis")
                st.markdown(result['detailed_analysis'])
                
                # Send completion message to JavaScript
                js_code = f"""
                <script>
                    window.parent.postMessage({{
                        type: 'analysis_complete',
                        data: {{ frame_count: {result['frame_count']} }}
                    }}, '*');
                </script>
                """
                components.html(js_code, height=0)

def analyze_captured_frame(frame_data):
    """Analyze a captured frame"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(frame_data['frame_data'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Analyze with AI Vision
        ai_vision = AIVisionAnalyzer()
        analysis = ai_vision.analyze_facial_expressions(image_array)
        
        # Get expressions
        expressions = analysis.get('facial_expressions', [])
        expressions_text = ', '.join(expressions) if expressions else 'neutral expression'
        
        # Generate detailed analysis
        detailed_analysis = analyze_expression(f"Interview context: {expressions_text}")
        
        # Track usage
        UsageTracker.track_analysis("screen_interview", st.session_state.get('user_id'))
        
        return {
            'frame_count': frame_data.get('frame_count', 0),
            'expressions': expressions_text,
            'emotion': analysis.get('emotional_state', 'neutral'),
            'confidence': analysis.get('confidence_level', 'medium'),
            'detailed_analysis': detailed_analysis
        }
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

if __name__ == "__main__":
    simple_screen_recorder()