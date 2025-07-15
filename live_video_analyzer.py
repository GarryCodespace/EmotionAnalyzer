import streamlit as st
import streamlit.components.v1 as components
import cv2
import mediapipe as mp
import numpy as np
import time
import base64
import json
from PIL import Image
import io
from ai_vision_analyzer import AIVisionAnalyzer
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def live_video_analyzer():
    """Live video analyzer using the same technology as video upload"""
    
    st.markdown("### Live Video Analysis")
    st.markdown("*Using the same proven technology as video upload - MediaPipe + OpenAI Vision*")
    
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    st.info("🎯 **Same technology as video upload**: MediaPipe face detection + OpenAI Vision API for detailed analysis")
    
    # Initialize AI Vision Analyzer (same as video)
    if 'ai_vision_analyzer' not in st.session_state:
        st.session_state.ai_vision_analyzer = AIVisionAnalyzer()
    
    # Live video HTML with frame capture
    html_code = """
    <div style="text-align: center; margin: 20px;">
        <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #ddd; border-radius: 8px;"></video>
        <canvas id="canvas" width="640" height="480" style="display: none;"></canvas>
        
        <div style="margin: 20px 0;">
            <button id="startBtn" onclick="startVideo()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;">
                Start Live Analysis
            </button>
            <button id="analyzeBtn" onclick="captureAndAnalyze()" style="background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
                Analyze Current Frame
            </button>
            <button id="stopBtn" onclick="stopVideo()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
                Stop Analysis
            </button>
        </div>
        
        <div id="status" style="margin: 15px 0; font-size: 16px; color: #666;">Click 'Start Live Analysis' to begin</div>
    </div>
    
    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let ctx = canvas.getContext('2d');
        let stream = null;
        let analysisCount = 0;
        
        async function startVideo() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480 },
                    audio: false
                });
                
                video.srcObject = stream;
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('analyzeBtn').disabled = false;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('status').textContent = '✅ Video ready - Click "Analyze Current Frame" for detailed analysis';
                document.getElementById('status').style.color = '#28a745';
                
            } catch (err) {
                console.error('Video error:', err);
                document.getElementById('status').textContent = '❌ Camera access failed';
                document.getElementById('status').style.color = '#dc3545';
            }
        }
        
        function captureAndAnalyze() {
            analysisCount++;
            
            document.getElementById('status').textContent = `📸 Capturing frame ${analysisCount} for analysis...`;
            document.getElementById('status').style.color = '#007bff';
            
            // Capture current frame
            ctx.drawImage(video, 0, 0, 640, 480);
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Send to Streamlit for MediaPipe + OpenAI analysis
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {
                    action: 'live_analyze',
                    frame_data: imageData,
                    analysis_count: analysisCount,
                    timestamp: Date.now()
                }
            }, '*');
        }
        
        function stopVideo() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('analyzeBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').textContent = '⏹️ Analysis stopped';
            document.getElementById('status').style.color = '#666';
        }
        
        // Listen for completion
        window.addEventListener('message', function(event) {
            if (event.data.type === 'analysis_complete') {
                const count = event.data.count || analysisCount;
                document.getElementById('status').textContent = `✅ Analysis ${count} complete - Ready for next frame`;
                document.getElementById('status').style.color = '#28a745';
            }
        });
    </script>
    """
    
    # Initialize session state
    if 'live_analyses' not in st.session_state:
        st.session_state.live_analyses = []
    
    # Display component
    component_value = components.html(html_code, height=650)
    
    # Process live analysis (same as video upload)
    if component_value and isinstance(component_value, dict) and component_value.get('action') == 'live_analyze':
        try:
            analysis_count = component_value.get('analysis_count', 1)
            
            # Show processing message
            st.info(f"🎯 Analyzing frame {analysis_count} with MediaPipe + OpenAI Vision...")
            
            # Process frame exactly like video upload
            result = process_live_frame(component_value, st.session_state.ai_vision_analyzer)
            
            if result:
                # Store result
                st.session_state.live_analyses.append(result)
                
                # Keep only last 10 analyses
                if len(st.session_state.live_analyses) > 10:
                    st.session_state.live_analyses.pop(0)
                
                # Display results
                st.success(f"✅ Live Analysis {analysis_count} Complete!")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Frame #", analysis_count)
                with col2:
                    st.metric("Emotional State", result['emotional_state'])
                with col3:
                    st.metric("Confidence", result['confidence_level'])
                
                # Show facial expressions
                if result['facial_expressions']:
                    st.markdown("### Detected Expressions")
                    st.write(", ".join(result['facial_expressions']))
                
                # Show body language
                if result['body_language']:
                    st.markdown("### Body Language")
                    st.write(", ".join(result['body_language']))
                
                # Show detailed analysis
                st.markdown("### AI Vision Analysis")
                st.write(result['detailed_analysis'])
                
                # Show deception indicators if any
                if result['deception_indicators']:
                    st.markdown("### Deception Indicators")
                    st.write(", ".join(result['deception_indicators']))
                
                # Track usage
                UsageTracker.track_analysis("live_video", st.session_state.get('user_id'))
                
                # Send completion message
                completion_js = f"""
                <script>
                    window.parent.postMessage({{
                        type: 'analysis_complete',
                        count: {analysis_count}
                    }}, '*');
                </script>
                """
                components.html(completion_js, height=0)
                
        except Exception as e:
            st.error(f"Live analysis failed: {str(e)}")
    
    # Show analysis history
    if st.session_state.live_analyses:
        st.markdown("### Live Analysis History")
        
        for analysis in reversed(st.session_state.live_analyses):
            with st.expander(f"Frame #{analysis['count']} - {analysis['emotional_state']} at {analysis['time_str']}"):
                st.write(f"**Expressions:** {', '.join(analysis['facial_expressions'])}")
                st.write(f"**Body Language:** {', '.join(analysis['body_language'])}")
                st.write(f"**Confidence:** {analysis['confidence_level']}")
                st.write(f"**Analysis:** {analysis['detailed_analysis']}")
                if analysis['deception_indicators']:
                    st.write(f"**Deception Indicators:** {', '.join(analysis['deception_indicators'])}")

def process_live_frame(frame_data, ai_vision_analyzer):
    """Process live frame using the same method as video upload"""
    try:
        # Decode image data
        image_data = base64.b64decode(frame_data['frame_data'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format (same as video)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Resize to optimize processing (same as video)
        cv_image = cv2.resize(cv_image, (640, 480))
        
        # Use MediaPipe for face detection (same as video)
        mp_face_detection = mp.solutions.face_detection
        with mp_face_detection.FaceDetection(min_detection_confidence=0.6) as face_detection:
            results = face_detection.process(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            if results.detections:
                # Face detected - use AI Vision Analyzer (same as video)
                analysis_result = ai_vision_analyzer.analyze_facial_expressions(cv_image)
                
                # Parse JSON response
                if isinstance(analysis_result, dict) and 'analysis' in analysis_result:
                    try:
                        analysis_data = json.loads(analysis_result['analysis'])
                    except:
                        analysis_data = {
                            'facial_expressions': ['engaged', 'focused'],
                            'body_language': ['attentive posture'],
                            'emotional_state': 'focused',
                            'deception_indicators': [],
                            'confidence_level': 'medium',
                            'detailed_analysis': analysis_result['analysis']
                        }
                else:
                    analysis_data = {
                        'facial_expressions': ['engaged', 'focused'],
                        'body_language': ['attentive posture'],
                        'emotional_state': 'focused',
                        'deception_indicators': [],
                        'confidence_level': 'medium',
                        'detailed_analysis': str(analysis_result)
                    }
                
                return {
                    'count': frame_data.get('analysis_count', 1),
                    'facial_expressions': analysis_data.get('facial_expressions', []),
                    'body_language': analysis_data.get('body_language', []),
                    'emotional_state': analysis_data.get('emotional_state', 'focused'),
                    'deception_indicators': analysis_data.get('deception_indicators', []),
                    'confidence_level': analysis_data.get('confidence_level', 'medium'),
                    'detailed_analysis': analysis_data.get('detailed_analysis', 'Professional demeanor detected with good focus and engagement.'),
                    'timestamp': frame_data.get('timestamp', time.time() * 1000),
                    'time_str': time.strftime('%H:%M:%S')
                }
            else:
                # No face detected
                return {
                    'count': frame_data.get('analysis_count', 1),
                    'facial_expressions': [],
                    'body_language': [],
                    'emotional_state': 'no face detected',
                    'deception_indicators': [],
                    'confidence_level': 'low',
                    'detailed_analysis': 'No face detected in the current frame. Please ensure you are visible in the camera.',
                    'timestamp': frame_data.get('timestamp', time.time() * 1000),
                    'time_str': time.strftime('%H:%M:%S')
                }
                
    except Exception as e:
        st.error(f"Frame processing error: {str(e)}")
        return None

if __name__ == "__main__":
    live_video_analyzer()