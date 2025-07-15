import streamlit as st
import streamlit.components.v1 as components
import time
from ai_vision_analyzer import AIVisionAnalyzer
from database import save_emotion_analysis
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def create_screen_recorder_component():
    """Create a screen recording component for interviews"""
    
    screen_recorder_html = """
    <div id="screen-recorder-container" style="text-align: center; margin: 20px 0; padding-bottom: 50px; min-height: 100vh;">
        <div id="screen-display" style="position: relative; display: inline-block;">
            <video id="screenVideo" width="800" height="600" autoplay muted playsinline style="border: 2px solid #ddd; border-radius: 8px; background: #f0f0f0;"></video>
            <canvas id="screenCanvas" width="800" height="600" style="display: none;"></canvas>
            
            <!-- Analysis overlay -->
            <div id="analysisOverlay" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-size: 14px; display: none; max-width: 300px;">
                <div id="overlayStatus" style="font-weight: bold; color: #4CAF50;">Ready</div>
                <div id="overlayExpressions" style="margin-top: 5px;">No expressions detected</div>
                <div id="overlayEmotion" style="margin-top: 5px;">Emotion: Neutral</div>
                <div id="overlayConfidence" style="margin-top: 5px;">Confidence: Medium</div>
            </div>
        </div>
        
        <br><br>
        <div style="margin: 10px 0;">
            <button id="startScreenBtn" onclick="startScreenRecording()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;">🖥️ Start Screen Recording</button>
            <button id="stopScreenBtn" onclick="stopScreenRecording()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>⏹️ Stop Recording</button>
            <button id="toggleScreenAnalysisBtn" onclick="toggleScreenAnalysis()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 8px; cursor: pointer; font-size: 16px;" disabled>🔍 Start Analysis</button>
        </div>
        
        <div style="margin: 10px 0;">
            <label style="font-weight: bold;">Analysis Settings: </label>
            <select id="screenAnalysisInterval" style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 0 10px;">
                <option value="5000">Every 5 seconds</option>
                <option value="10000" selected>Every 10 seconds</option>
                <option value="15000">Every 15 seconds</option>
                <option value="30000">Every 30 seconds</option>
            </select>
            <label style="margin-left: 20px;">
                <input type="checkbox" id="showOverlay" checked> Show analysis overlay
            </label>
        </div>
        
        <div id="screenStatus" style="margin: 15px 0; font-weight: bold; color: #666; font-size: 16px;">Click 'Start Screen Recording' to begin</div>
        
        <div id="interviewTips" style="margin: 20px 0; padding: 20px; background: #e3f2fd; border-radius: 8px; text-align: left; min-height: 150px; overflow: visible;">
            <h4 style="margin-top: 0; margin-bottom: 15px; color: #1976d2;">Interview Tips:</h4>
            <ul style="margin: 10px 0; padding-left: 20px; line-height: 1.6;">
                <li style="margin-bottom: 8px;">Start recording before joining your video interview</li>
                <li style="margin-bottom: 8px;">The analysis overlay shows your emotional state in real-time</li>
                <li style="margin-bottom: 8px;">Use insights to maintain confident and positive expressions</li>
                <li style="margin-bottom: 8px;">Perfect for Zoom, Teams, Google Meet, and other video platforms</li>
            </ul>
        </div>
    </div>

    <script>
        let screenVideo = document.getElementById('screenVideo');
        let screenCanvas = document.getElementById('screenCanvas');
        let screenContext = screenCanvas.getContext('2d');
        let screenStream = null;
        let screenAnalysisInterval = null;
        let isScreenAnalysisActive = false;
        let screenFrameCount = 0;

        async function startScreenRecording() {
            try {
                const displayMediaOptions = {
                    video: {
                        width: { ideal: 1920 },
                        height: { ideal: 1080 },
                        frameRate: { ideal: 30 }
                    },
                    audio: false
                };
                
                screenStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);
                screenVideo.srcObject = screenStream;
                
                // Handle stream ending
                screenStream.getVideoTracks()[0].addEventListener('ended', () => {
                    stopScreenRecording();
                });
                
                document.getElementById('startScreenBtn').disabled = true;
                document.getElementById('stopScreenBtn').disabled = false;
                document.getElementById('toggleScreenAnalysisBtn').disabled = false;
                document.getElementById('screenStatus').textContent = '✅ Screen recording active - Click "Start Analysis" for emotion analysis';
                document.getElementById('screenStatus').style.color = '#28a745';
                
            } catch (err) {
                console.error('Error starting screen recording:', err);
                let errorMsg = 'Screen recording failed';
                if (err.name === 'NotAllowedError') {
                    errorMsg = 'Screen recording permission denied. Please allow screen sharing and try again.';
                } else if (err.name === 'NotSupportedError') {
                    errorMsg = 'Screen recording not supported in this browser. Try Chrome or Firefox.';
                }
                document.getElementById('screenStatus').textContent = '❌ ' + errorMsg;
                document.getElementById('screenStatus').style.color = '#dc3545';
            }
        }

        function stopScreenRecording() {
            if (screenStream) {
                screenStream.getTracks().forEach(track => track.stop());
                screenVideo.srcObject = null;
                screenStream = null;
            }
            
            stopScreenAnalysis();
            
            document.getElementById('startScreenBtn').disabled = false;
            document.getElementById('stopScreenBtn').disabled = true;
            document.getElementById('toggleScreenAnalysisBtn').disabled = true;
            document.getElementById('screenStatus').textContent = '⏹️ Screen recording stopped';
            document.getElementById('screenStatus').style.color = '#666';
            document.getElementById('analysisOverlay').style.display = 'none';
        }

        function toggleScreenAnalysis() {
            if (isScreenAnalysisActive) {
                stopScreenAnalysis();
            } else {
                startScreenAnalysis();
            }
        }

        function startScreenAnalysis() {
            if (!screenStream) return;
            
            isScreenAnalysisActive = true;
            document.getElementById('toggleScreenAnalysisBtn').textContent = '⏸️ Stop Analysis';
            document.getElementById('toggleScreenAnalysisBtn').style.background = '#ffc107';
            document.getElementById('screenStatus').textContent = '🔍 Live interview analysis active';
            document.getElementById('screenStatus').style.color = '#007bff';
            
            const showOverlay = document.getElementById('showOverlay').checked;
            if (showOverlay) {
                document.getElementById('analysisOverlay').style.display = 'block';
            }
            
            const intervalMs = parseInt(document.getElementById('screenAnalysisInterval').value);
            
            screenAnalysisInterval = setInterval(() => {
                if (isScreenAnalysisActive && screenStream) {
                    captureAndAnalyzeScreen();
                }
            }, intervalMs);
        }

        function stopScreenAnalysis() {
            if (screenAnalysisInterval) {
                clearInterval(screenAnalysisInterval);
                screenAnalysisInterval = null;
            }
            
            isScreenAnalysisActive = false;
            document.getElementById('toggleScreenAnalysisBtn').textContent = '🔍 Start Analysis';
            document.getElementById('toggleScreenAnalysisBtn').style.background = '#28a745';
            document.getElementById('screenStatus').textContent = '✅ Screen recording active - Analysis stopped';
            document.getElementById('screenStatus').style.color = '#28a745';
            document.getElementById('analysisOverlay').style.display = 'none';
        }

        function captureAndAnalyzeScreen() {
            try {
                screenFrameCount++;
                
                // Draw current screen frame to canvas
                screenContext.drawImage(screenVideo, 0, 0, screenCanvas.width, screenCanvas.height);
                
                // Convert canvas to base64
                const imageData = screenCanvas.toDataURL('image/jpeg', 0.8);
                
                // Update overlay status
                document.getElementById('overlayStatus').textContent = `Analyzing frame ${screenFrameCount}...`;
                
                // Send frame data to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: {
                        screen_frame: imageData,
                        frame_count: screenFrameCount,
                        timestamp: Date.now(),
                        analysis_type: 'interview'
                    }
                }, '*');
                
                // Update status
                document.getElementById('screenStatus').textContent = `🔍 Analyzing interview frame ${screenFrameCount}...`;
                
            } catch (err) {
                console.error('Error capturing screen frame:', err);
                document.getElementById('screenStatus').textContent = '❌ Error capturing screen frame';
                document.getElementById('screenStatus').style.color = '#dc3545';
            }
        }

        // Listen for analysis results from Streamlit
        window.addEventListener('message', function(event) {
            if (event.data.type === 'screen_analysis_result') {
                const result = event.data.data;
                
                // Update overlay
                document.getElementById('overlayStatus').textContent = `Frame ${result.frame_count || screenFrameCount}`;
                document.getElementById('overlayExpressions').textContent = 'Expressions: ' + (result.expressions || 'None detected');
                document.getElementById('overlayEmotion').textContent = 'Emotion: ' + (result.emotion || 'Neutral');
                document.getElementById('overlayConfidence').textContent = 'Confidence: ' + (result.confidence || 'Medium');
                
                // Update main status
                document.getElementById('screenStatus').textContent = 
                    `✅ Interview analysis complete (Frame ${result.frame_count || screenFrameCount}) - ${result.emotion || 'Neutral'}`;
                document.getElementById('screenStatus').style.color = '#28a745';
            }
        });

        // Show interview tips initially
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('interviewTips').style.display = 'block';
        });
    </script>
    """
    
    return screen_recorder_html

def show_screen_recorder_interview():
    """Display screen recording interface for interviews"""
    
    st.markdown("### Screen Recording for Interviews")
    st.markdown("*Record your screen during video interviews with real-time emotion analysis*")
    
    # Check daily usage limit
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    # Instructions
    st.info("🎯 **Perfect for Job Interviews**: Record your screen during video interviews and get real-time feedback on your emotional expressions and confidence levels!")
    
    # Create screen recorder component
    screen_recorder_html = create_screen_recorder_component()
    
    # Display component and get frame data
    component_value = components.html(screen_recorder_html, height=1200)
    
    # Process screen frame data
    if component_value and isinstance(component_value, dict):
        if 'screen_frame' in component_value:
            process_screen_frame(component_value)
    
    # Display recent analysis results
    if 'screen_analysis_results' in st.session_state and st.session_state.screen_analysis_results:
        st.markdown("### Interview Analysis Results")
        
        # Show latest result prominently
        latest = st.session_state.screen_analysis_results[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Frame #", latest['frame_count'])
        with col2:
            st.metric("Expressions", latest['expressions'])
        with col3:
            st.metric("Emotion", latest['emotion'])
        with col4:
            st.metric("Confidence", latest['confidence'])
        
        # Show detailed analysis
        with st.expander("Detailed Interview Analysis"):
            st.write(f"**Full Analysis**: {latest['detailed_analysis']}")
            st.write(f"**Recommendations**: {latest.get('recommendations', 'Maintain current expression and confidence level.')}")
        
        # Show analysis timeline
        with st.expander(f"Interview Timeline ({len(st.session_state.screen_analysis_results)} analyses)"):
            for i, result in enumerate(reversed(st.session_state.screen_analysis_results)):
                timestamp = time.strftime('%H:%M:%S', time.localtime(result['timestamp']/1000))
                st.write(f"**{timestamp} - Frame #{result['frame_count']}**: {result['emotion']} - {result['expressions']} ({result['confidence']})")
                if i < 3:  # Show details for recent results
                    st.write(f"*Analysis*: {result['detailed_analysis'][:100]}...")
                st.write("---")

def process_screen_frame(frame_data):
    """Process captured screen frame for interview analysis"""
    
    try:
        # Check daily usage limit
        if not check_daily_limit(show_upgrade_prompt=False):
            return
        
        # Decode base64 image
        import base64
        from PIL import Image
        import io
        import numpy as np
        
        # Extract image data
        image_data_url = frame_data['screen_frame']
        image_data = base64.b64decode(image_data_url.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Analyze with AI Vision
        ai_vision = AIVisionAnalyzer()
        
        # Enhanced analysis for interview context
        context_prompt = """
        This is a screen recording during a job interview. Analyze the person's facial expressions and body language 
        for interview performance. Focus on:
        - Confidence and professionalism
        - Engagement and attentiveness  
        - Stress or anxiety indicators
        - Authenticity and genuineness
        - Overall interview presence
        
        Provide specific feedback for interview improvement.
        """
        
        analysis = ai_vision.analyze_emotion_context(image_array, [context_prompt])
        
        # Track usage
        UsageTracker.track_analysis("screen_interview", st.session_state.get('user_id'))
        
        # Prepare results for display
        expressions = analysis.get('facial_expressions', [])
        expressions_text = ', '.join(expressions) if expressions else 'Professional demeanor'
        
        emotional_state = analysis.get('emotional_state', 'confident')
        confidence_level = analysis.get('confidence_level', 'good')
        detailed_analysis = analysis.get('detailed_analysis', 'Maintaining professional appearance')
        
        # Generate interview-specific recommendations
        recommendations = generate_interview_recommendations(expressions, emotional_state, confidence_level)
        
        # Store results in session state
        if 'screen_analysis_results' not in st.session_state:
            st.session_state.screen_analysis_results = []
        
        result = {
            'frame_count': frame_data.get('frame_count', 0),
            'timestamp': frame_data.get('timestamp', time.time() * 1000),
            'expressions': expressions_text,
            'emotion': emotional_state,
            'confidence': confidence_level,
            'detailed_analysis': detailed_analysis,
            'recommendations': recommendations
        }
        
        # Keep only last 10 results for interviews
        st.session_state.screen_analysis_results.append(result)
        if len(st.session_state.screen_analysis_results) > 10:
            st.session_state.screen_analysis_results.pop(0)
        
        # Save to database if logged in
        if st.session_state.get('logged_in', False):
            save_emotion_analysis(
                session_id=st.session_state.session_id,
                expressions=expressions,
                ai_analysis=f"Interview Analysis: {detailed_analysis}. Recommendations: {recommendations}",
                analysis_type="screen_interview"
            )
        
        # Send results back to JavaScript
        js_code = f"""
        <script>
            setTimeout(function() {{
                window.parent.postMessage({{
                    type: 'screen_analysis_result',
                    data: {{
                        expressions: '{expressions_text}',
                        emotion: '{emotional_state}',
                        confidence: '{confidence_level}',
                        frame_count: {result['frame_count']}
                    }}
                }}, '*');
            }}, 100);
        </script>
        """
        
        components.html(js_code, height=0)
        
    except Exception as e:
        st.error(f"Error processing screen frame: {str(e)}")

def generate_interview_recommendations(expressions, emotion, confidence):
    """Generate specific recommendations for interview performance"""
    
    recommendations = []
    
    # Confidence recommendations
    if confidence in ['low', 'very low']:
        recommendations.append("Maintain eye contact and sit up straight to project confidence")
    elif confidence == 'high':
        recommendations.append("Great confidence level - maintain this energy")
    
    # Emotional state recommendations
    if emotion in ['nervous', 'anxious', 'stressed']:
        recommendations.append("Take deep breaths and speak slowly to reduce anxiety")
    elif emotion in ['happy', 'positive', 'engaged']:
        recommendations.append("Excellent positive energy - keep this enthusiasm")
    elif emotion == 'neutral':
        recommendations.append("Consider showing more engagement and enthusiasm")
    
    # Expression-specific recommendations
    if 'smile' in str(expressions).lower():
        recommendations.append("Natural smile detected - great for building rapport")
    elif 'frown' in str(expressions).lower():
        recommendations.append("Try to maintain a neutral or slightly positive expression")
    
    if not recommendations:
        recommendations.append("Maintain current professional demeanor")
    
    return "; ".join(recommendations)

def init_screen_recorder_interview():
    """Initialize screen recorder interview session state"""
    if 'screen_analysis_results' not in st.session_state:
        st.session_state.screen_analysis_results = []
    if 'interview_session_active' not in st.session_state:
        st.session_state.interview_session_active = False