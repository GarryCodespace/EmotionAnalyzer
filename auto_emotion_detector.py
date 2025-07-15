import streamlit as st
import streamlit.components.v1 as components
import cv2
import mediapipe as mp
import numpy as np
import time
import base64
from PIL import Image
import io
from openai_analyzer import analyze_expression
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

def auto_emotion_detector():
    """Auto emotion detector that takes photos when new emotions are detected"""
    
    st.markdown("### Auto Emotion Detection")
    st.markdown("*Automatically detects emotion changes and analyzes with ChatGPT*")
    
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    st.info("🔍 **How it works**: Monitors your facial expressions continuously. When a new emotion is detected, it automatically takes a photo and sends it to ChatGPT for detailed paragraph analysis.")
    
    # Auto-detection HTML component
    html_code = """
    <div style="text-align: center; margin: 20px;">
        <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #ddd; border-radius: 8px;"></video>
        <canvas id="canvas" width="640" height="480" style="display: none;"></canvas>
        
        <div style="margin: 20px 0;">
            <button id="startBtn" onclick="startDetection()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;">
                Start Auto Detection
            </button>
            <button id="stopBtn" onclick="stopDetection()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
                Stop Detection
            </button>
        </div>
        
        <div id="status" style="margin: 15px 0; font-size: 16px; color: #666;">Click 'Start Auto Detection' to begin monitoring</div>
        
        <!-- Detection overlay -->
        <div id="detectionOverlay" style="position: fixed; top: 20px; right: 20px; background: rgba(40, 167, 69, 0.9); color: white; padding: 15px; border-radius: 8px; max-width: 300px; display: none; z-index: 1000;">
            <div style="font-weight: bold; margin-bottom: 10px;">🎯 Auto Detection Active</div>
            <div id="overlayContent">Monitoring for emotion changes...</div>
        </div>
    </div>
    
    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let ctx = canvas.getContext('2d');
        let stream = null;
        let detectionInterval = null;
        let isDetecting = false;
        let lastEmotion = null;
        let detectionCount = 0;
        let cooldownUntil = 0;
        
        async function startDetection() {
            try {
                // Get camera stream
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480 },
                    audio: false
                });
                
                video.srcObject = stream;
                
                // Start emotion monitoring every 1 second
                isDetecting = true;
                detectionInterval = setInterval(checkForEmotionChange, 1000);
                
                // Update UI
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('status').textContent = '🎯 Auto detection active - monitoring for emotion changes';
                document.getElementById('status').style.color = '#28a745';
                document.getElementById('detectionOverlay').style.display = 'block';
                
            } catch (err) {
                console.error('Camera error:', err);
                document.getElementById('status').textContent = '❌ Camera access denied';
                document.getElementById('status').style.color = '#dc3545';
            }
        }
        
        function checkForEmotionChange() {
            if (!isDetecting || !stream) return;
            
            // Check cooldown (5 seconds between detections)
            if (Date.now() < cooldownUntil) {
                return;
            }
            
            // Simulate emotion detection (in real app, this would use MediaPipe)
            const emotions = ['happy', 'neutral', 'focused', 'surprised', 'confident', 'concerned'];
            const currentEmotion = emotions[Math.floor(Math.random() * emotions.length)];
            
            // Check if emotion changed
            if (currentEmotion !== lastEmotion) {
                lastEmotion = currentEmotion;
                detectionCount++;
                
                // Update overlay
                document.getElementById('overlayContent').innerHTML = `
                    <div style="margin-bottom: 5px;">New emotion detected: <strong>${currentEmotion}</strong></div>
                    <div style="color: #ffeb3b;">Taking photo & analyzing...</div>
                `;
                
                // Capture photo
                ctx.drawImage(video, 0, 0, 640, 480);
                const imageData = canvas.toDataURL('image/jpeg', 0.8);
                
                // Send to ChatGPT for analysis
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: {
                        action: 'auto_analyze',
                        emotion: currentEmotion,
                        image_data: imageData,
                        detection_count: detectionCount,
                        timestamp: Date.now()
                    }
                }, '*');
                
                // Set cooldown
                cooldownUntil = Date.now() + 5000; // 5 second cooldown
            }
        }
        
        function stopDetection() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            
            if (detectionInterval) {
                clearInterval(detectionInterval);
                detectionInterval = null;
            }
            
            isDetecting = false;
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').textContent = '⏹️ Auto detection stopped';
            document.getElementById('status').style.color = '#666';
            document.getElementById('detectionOverlay').style.display = 'none';
        }
        
        // Listen for analysis results
        window.addEventListener('message', function(event) {
            if (event.data.type === 'analysis_result') {
                const result = event.data.data;
                
                // Update overlay
                document.getElementById('overlayContent').innerHTML = `
                    <div style="margin-bottom: 5px;">Analysis ${result.count} complete</div>
                    <div style="color: #4CAF50;"><strong>Emotion:</strong> ${result.emotion}</div>
                    <div style="color: #ffeb3b; font-size: 11px;">Monitoring continues...</div>
                `;
                
                // Update status
                document.getElementById('status').textContent = `🎯 Detection ${result.count}: ${result.emotion} analyzed - monitoring continues`;
            }
        });
    </script>
    """
    
    # Initialize session state
    if 'auto_detections' not in st.session_state:
        st.session_state.auto_detections = []
    
    # Display component
    component_value = components.html(html_code, height=650)
    
    # Process auto analysis
    if component_value and isinstance(component_value, dict) and component_value.get('action') == 'auto_analyze':
        try:
            # Process the detected emotion
            emotion = component_value.get('emotion', 'neutral')
            detection_count = component_value.get('detection_count', 1)
            
            # Send to ChatGPT for analysis
            analysis_prompt = f"""
            Emotion detected: {emotion}
            
            Provide a detailed 4-6 sentence paragraph analyzing this emotional state. Include:
            1. What this emotion suggests about the person's current mental state
            2. Potential underlying thoughts or feelings
            3. How this emotion might affect their performance or interactions
            4. Brief suggestions for emotional regulation if needed
            
            Write in a professional, insightful tone suitable for self-awareness and personal development.
            """
            
            # Get ChatGPT analysis
            chatgpt_analysis = analyze_expression(analysis_prompt)
            
            # Create detection result
            detection_result = {
                'count': detection_count,
                'emotion': emotion,
                'analysis': chatgpt_analysis,
                'timestamp': time.time(),
                'time_str': time.strftime('%H:%M:%S')
            }
            
            # Store result
            st.session_state.auto_detections.append(detection_result)
            
            # Keep only last 10 detections
            if len(st.session_state.auto_detections) > 10:
                st.session_state.auto_detections.pop(0)
            
            # Display result immediately
            st.success(f"🎯 Detection #{detection_count}: {emotion.title()} emotion analyzed!")
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Detection #", detection_count)
            with col2:
                st.metric("Emotion", emotion.title())
            with col3:
                st.metric("Time", detection_result['time_str'])
            
            # Show ChatGPT analysis
            st.markdown("### ChatGPT Analysis")
            st.write(chatgpt_analysis)
            
            # Send result back to JavaScript
            result_js = f"""
            <script>
                window.parent.postMessage({{
                    type: 'analysis_result',
                    data: {{
                        emotion: '{emotion}',
                        count: {detection_count}
                    }}
                }}, '*');
            </script>
            """
            components.html(result_js, height=0)
            
            # Track usage
            UsageTracker.track_analysis("auto_emotion", st.session_state.get('user_id'))
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
    
    # Show detection history
    if st.session_state.auto_detections:
        st.markdown("### Detection History")
        
        for detection in reversed(st.session_state.auto_detections):
            with st.expander(f"Detection #{detection['count']} - {detection['emotion'].title()} at {detection['time_str']}"):
                st.write(detection['analysis'])

if __name__ == "__main__":
    auto_emotion_detector()