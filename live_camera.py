import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import time
import threading
import queue
from ai_vision_analyzer import AIVisionAnalyzer
from database import save_emotion_analysis
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def create_live_camera_component():
    """Create a live video streaming camera component"""
    
    camera_html = """
    <div id="live-camera-container" style="text-align: center; margin: 20px 0;">
        <video id="liveVideo" width="640" height="480" autoplay muted playsinline style="border: 2px solid #ddd; border-radius: 8px; background: #f0f0f0;"></video>
        <canvas id="liveCanvas" width="640" height="480" style="display: none;"></canvas>
        <br><br>
        <div style="margin: 10px 0;">
            <button id="startLiveBtn" onclick="startLiveCamera()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;">📹 Start Live Camera</button>
            <button id="stopLiveBtn" onclick="stopLiveCamera()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>⏹️ Stop Camera</button>
            <button id="toggleAnalysisBtn" onclick="toggleAnalysis()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>🔍 Start Analysis</button>
        </div>
        <div style="margin: 10px 0;">
            <label style="font-weight: bold;">Analysis Interval: </label>
            <select id="analysisInterval" style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 0 10px;">
                <option value="3000">Every 3 seconds</option>
                <option value="5000" selected>Every 5 seconds</option>
                <option value="10000">Every 10 seconds</option>
                <option value="15000">Every 15 seconds</option>
            </select>
        </div>
        <div id="liveStatus" style="margin: 15px 0; font-weight: bold; color: #666; font-size: 16px;">Click 'Start Live Camera' to begin</div>
        <div id="analysisResults" style="margin: 15px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; text-align: left; display: none;">
            <h4 style="margin-top: 0;">Latest Analysis:</h4>
            <div id="expressionResults"></div>
            <div id="emotionResults"></div>
            <div id="confidenceResults"></div>
        </div>
    </div>

    <script>
        let liveVideo = document.getElementById('liveVideo');
        let liveCanvas = document.getElementById('liveCanvas');
        let liveContext = liveCanvas.getContext('2d');
        let liveStream = null;
        let analysisInterval = null;
        let isAnalysisActive = false;
        let frameCount = 0;

        async function startLiveCamera() {
            try {
                const constraints = {
                    video: {
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        facingMode: 'user',
                        frameRate: { ideal: 30 }
                    }
                };
                
                liveStream = await navigator.mediaDevices.getUserMedia(constraints);
                liveVideo.srcObject = liveStream;
                
                document.getElementById('startLiveBtn').disabled = true;
                document.getElementById('stopLiveBtn').disabled = false;
                document.getElementById('toggleAnalysisBtn').disabled = false;
                document.getElementById('liveStatus').textContent = '✅ Live camera active - Click "Start Analysis" for AI analysis';
                document.getElementById('liveStatus').style.color = '#28a745';
                
            } catch (err) {
                console.error('Error accessing camera:', err);
                let errorMsg = 'Camera access denied or not available';
                if (err.name === 'NotAllowedError') {
                    errorMsg = 'Camera permission denied. Please allow camera access and try again.';
                } else if (err.name === 'NotFoundError') {
                    errorMsg = 'No camera found. Please connect a camera and try again.';
                }
                document.getElementById('liveStatus').textContent = '❌ ' + errorMsg;
                document.getElementById('liveStatus').style.color = '#dc3545';
            }
        }

        function stopLiveCamera() {
            if (liveStream) {
                liveStream.getTracks().forEach(track => track.stop());
                liveVideo.srcObject = null;
                liveStream = null;
            }
            
            stopAnalysis();
            
            document.getElementById('startLiveBtn').disabled = false;
            document.getElementById('stopLiveBtn').disabled = true;
            document.getElementById('toggleAnalysisBtn').disabled = true;
            document.getElementById('liveStatus').textContent = '⏹️ Camera stopped';
            document.getElementById('liveStatus').style.color = '#666';
            document.getElementById('analysisResults').style.display = 'none';
        }

        function toggleAnalysis() {
            if (isAnalysisActive) {
                stopAnalysis();
            } else {
                startAnalysis();
            }
        }

        function startAnalysis() {
            if (!liveStream) return;
            
            isAnalysisActive = true;
            document.getElementById('toggleAnalysisBtn').textContent = '⏸️ Stop Analysis';
            document.getElementById('toggleAnalysisBtn').style.background = '#ffc107';
            document.getElementById('liveStatus').textContent = '🔍 Live analysis active';
            document.getElementById('liveStatus').style.color = '#007bff';
            document.getElementById('analysisResults').style.display = 'block';
            
            const intervalMs = parseInt(document.getElementById('analysisInterval').value);
            
            analysisInterval = setInterval(() => {
                if (isAnalysisActive && liveStream) {
                    captureAndAnalyzeFrame();
                }
            }, intervalMs);
        }

        function stopAnalysis() {
            if (analysisInterval) {
                clearInterval(analysisInterval);
                analysisInterval = null;
            }
            
            isAnalysisActive = false;
            document.getElementById('toggleAnalysisBtn').textContent = '🔍 Start Analysis';
            document.getElementById('toggleAnalysisBtn').style.background = '#28a745';
            document.getElementById('liveStatus').textContent = '✅ Live camera active - Analysis stopped';
            document.getElementById('liveStatus').style.color = '#28a745';
        }

        function captureAndAnalyzeFrame() {
            try {
                frameCount++;
                
                // Draw current video frame to canvas
                liveContext.drawImage(liveVideo, 0, 0, liveCanvas.width, liveCanvas.height);
                
                // Convert canvas to base64
                const imageData = liveCanvas.toDataURL('image/jpeg', 0.8);
                
                // Send frame data to Streamlit with frame count
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: {
                        live_frame: imageData,
                        frame_count: frameCount,
                        timestamp: Date.now()
                    }
                }, '*');
                
                // Update status
                document.getElementById('liveStatus').textContent = `🔍 Analyzing frame ${frameCount}...`;
                
            } catch (err) {
                console.error('Error capturing frame:', err);
                document.getElementById('liveStatus').textContent = '❌ Error capturing frame';
                document.getElementById('liveStatus').style.color = '#dc3545';
            }
        }

        // Listen for analysis results from Streamlit
        window.addEventListener('message', function(event) {
            if (event.data.type === 'analysis_result') {
                const result = event.data.data;
                
                document.getElementById('expressionResults').innerHTML = 
                    '<strong>Expressions:</strong> ' + (result.expressions || 'None detected');
                document.getElementById('emotionResults').innerHTML = 
                    '<strong>Emotional State:</strong> ' + (result.emotion || 'Neutral');
                document.getElementById('confidenceResults').innerHTML = 
                    '<strong>Confidence:</strong> ' + (result.confidence || 'Medium');
                
                document.getElementById('liveStatus').textContent = 
                    `✅ Analysis complete (Frame ${result.frame_count || frameCount})`;
                document.getElementById('liveStatus').style.color = '#28a745';
            }
        });

        // Auto-start camera when component loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                if (document.getElementById('startLiveBtn') && !document.getElementById('startLiveBtn').disabled) {
                    startLiveCamera();
                }
            }, 1000);
        });
    </script>
    """
    
    return camera_html

def show_live_camera():
    """Display live camera interface with continuous video streaming"""
    
    st.markdown("### Live Video Analysis")
    st.markdown("*Continuous real-time emotion analysis with live video streaming*")
    
    # Check daily usage limit
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    # Instructions
    st.info("📹 **Instructions**: Camera will start automatically. Click 'Start Analysis' to begin continuous emotion analysis every few seconds!")
    
    # Create live camera component
    camera_html = create_live_camera_component()
    
    # Display camera component and get frame data
    component_value = components.html(camera_html, height=750)
    
    # Process live frame data
    if component_value and isinstance(component_value, dict):
        if 'live_frame' in component_value:
            process_live_frame(component_value)
    
    # Display recent analysis results
    if 'live_analysis_results' in st.session_state and st.session_state.live_analysis_results:
        st.markdown("### Recent Analysis Results")
        
        # Show latest result prominently
        latest = st.session_state.live_analysis_results[-1]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest Expressions", latest['expressions'])
        with col2:
            st.metric("Emotional State", latest['emotion'])
        with col3:
            st.metric("Confidence", latest['confidence'])
        
        # Show analysis history
        with st.expander(f"Analysis History ({len(st.session_state.live_analysis_results)} results)"):
            for i, result in enumerate(reversed(st.session_state.live_analysis_results)):
                st.write(f"**Frame #{result['frame_count']}**: {result['expressions']} - {result['emotion']} ({result['confidence']})")
                if i == 0:  # Show detailed analysis for latest result
                    st.write(f"*Detailed Analysis*: {result['detailed_analysis']}")
                st.write("---")

def process_live_frame(frame_data):
    """Process live video frame"""
    
    try:
        # Check daily usage limit
        if not check_daily_limit(show_upgrade_prompt=False):
            return
        
        # Decode base64 image
        import base64
        from PIL import Image
        import io
        
        # Extract image data
        image_data_url = frame_data['live_frame']
        image_data = base64.b64decode(image_data_url.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Analyze with AI Vision
        ai_vision = AIVisionAnalyzer()
        analysis = ai_vision.analyze_facial_expressions(image_array)
        
        # Track usage
        UsageTracker.track_analysis("live_camera", st.session_state.get('user_id'))
        
        # Save to database if logged in
        if st.session_state.get('logged_in', False):
            expressions = analysis.get('facial_expressions', [])
            detailed_analysis = analysis.get('detailed_analysis', 'No analysis available')
            save_emotion_analysis(
                session_id=st.session_state.session_id,
                expressions=expressions,
                ai_analysis=detailed_analysis,
                analysis_type="live_camera"
            )
        
        # Prepare results for display
        expressions = analysis.get('facial_expressions', [])
        expressions_text = ', '.join(expressions) if expressions else 'No expressions detected'
        
        emotional_state = analysis.get('emotional_state', 'neutral')
        confidence_level = analysis.get('confidence_level', 'medium')
        detailed_analysis = analysis.get('detailed_analysis', 'No detailed analysis available')
        
        # Store results in session state for display
        if 'live_analysis_results' not in st.session_state:
            st.session_state.live_analysis_results = []
        
        result = {
            'frame_count': frame_data.get('frame_count', 0),
            'timestamp': frame_data.get('timestamp', time.time() * 1000),
            'expressions': expressions_text,
            'emotion': emotional_state,
            'confidence': confidence_level,
            'detailed_analysis': detailed_analysis
        }
        
        # Keep only last 5 results
        st.session_state.live_analysis_results.append(result)
        if len(st.session_state.live_analysis_results) > 5:
            st.session_state.live_analysis_results.pop(0)
        
        # Display current analysis results
        st.success(f"**Live Analysis #{result['frame_count']} Complete!**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Expressions**: {expressions_text}")
            st.write(f"**Emotional State**: {emotional_state}")
        with col2:
            st.write(f"**Confidence**: {confidence_level}")
            st.write(f"**Frame**: #{result['frame_count']}")
        
        with st.expander("Detailed Analysis"):
            st.write(detailed_analysis)
        
        # Use JavaScript to update the component display
        js_code = f"""
        <script>
            setTimeout(function() {{
                try {{
                    if (parent.document.getElementById('expressionResults')) {{
                        parent.document.getElementById('expressionResults').innerHTML = 
                            '<strong>Expressions:</strong> {expressions_text}';
                        parent.document.getElementById('emotionResults').innerHTML = 
                            '<strong>Emotional State:</strong> {emotional_state}';
                        parent.document.getElementById('confidenceResults').innerHTML = 
                            '<strong>Confidence:</strong> {confidence_level}';
                        parent.document.getElementById('liveStatus').textContent = 
                            '✅ Analysis #{result['frame_count']} complete - {expressions_text}';
                        parent.document.getElementById('liveStatus').style.color = '#28a745';
                    }}
                }} catch(e) {{
                    console.log('Could not update parent elements:', e);
                }}
            }}, 100);
        </script>
        """
        
        components.html(js_code, height=0)
        
    except Exception as e:
        st.error(f"Error processing live frame: {str(e)}")

def init_live_camera():
    """Initialize live camera session state"""
    if 'live_camera_active' not in st.session_state:
        st.session_state.live_camera_active = False
    if 'live_frame_count' not in st.session_state:
        st.session_state.live_frame_count = 0