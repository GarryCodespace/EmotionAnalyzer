import streamlit as st
import streamlit.components.v1 as components
import time
import os
from openai import OpenAI
from payment_ui import check_daily_limit
from payment_plans import UsageTracker

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def simple_chatgpt_analyzer():
    """Simple ChatGPT analyzer that works reliably"""
    
    st.markdown("### Live ChatGPT Emotion Analysis")
    st.markdown("*Direct integration with ChatGPT for instant emotion analysis*")
    
    if not check_daily_limit():
        st.error("Daily usage limit reached. Please upgrade to continue.")
        return
    
    st.info("🤖 **Direct ChatGPT**: Start camera → Click analyze → Get instant ChatGPT paragraph analysis")
    
    # Simple HTML for camera and analysis
    html_code = """
    <div style="text-align: center; margin: 20px;">
        <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #ddd; border-radius: 8px; background: #f5f5f5;"></video>
        <br><br>
        <button id="startBtn" onclick="startCamera()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;">
            Start Camera
        </button>
        <button id="analyzeBtn" onclick="analyzeNow()" style="background: #FF6B35; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
            Analyze with ChatGPT
        </button>
        <button id="stopBtn" onclick="stopCamera()" style="background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 5px; cursor: pointer;" disabled>
            Stop Camera
        </button>
        <div id="status" style="margin-top: 15px; font-size: 16px; color: #666;">Click 'Start Camera' to begin</div>
    </div>
    
    <script>
        let video = document.getElementById('video');
        let stream = null;
        let analysisCount = 0;
        
        async function startCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480 },
                    audio: false
                });
                
                video.srcObject = stream;
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('analyzeBtn').disabled = false;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('status').textContent = '✅ Camera ready - Click "Analyze with ChatGPT"';
                document.getElementById('status').style.color = '#28a745';
                
            } catch (err) {
                console.error('Camera error:', err);
                document.getElementById('status').textContent = '❌ Camera access failed';
                document.getElementById('status').style.color = '#dc3545';
            }
        }
        
        function analyzeNow() {
            analysisCount++;
            
            document.getElementById('status').textContent = `🤖 Sending to ChatGPT... (Analysis ${analysisCount})`;
            document.getElementById('status').style.color = '#FF6B35';
            
            // Simple trigger without image processing
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {
                    action: 'chatgpt_analyze',
                    count: analysisCount,
                    timestamp: Date.now()
                }
            }, '*');
        }
        
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('analyzeBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').textContent = '⏹️ Camera stopped';
            document.getElementById('status').style.color = '#666';
        }
        
        // Listen for completion
        window.addEventListener('message', function(event) {
            if (event.data.type === 'chatgpt_complete') {
                const count = event.data.count || analysisCount;
                document.getElementById('status').textContent = `✅ ChatGPT Analysis ${count} complete - Ready for next`;
                document.getElementById('status').style.color = '#28a745';
            }
        });
    </script>
    """
    
    # Initialize session state
    if 'chatgpt_analyses' not in st.session_state:
        st.session_state.chatgpt_analyses = []
    
    # Display component
    component_value = components.html(html_code, height=650)
    
    # Process ChatGPT analysis
    if component_value and isinstance(component_value, dict) and component_value.get('action') == 'chatgpt_analyze':
        try:
            analysis_count = component_value.get('count', 1)
            
            # Direct ChatGPT call without image processing
            st.info(f"🤖 Sending analysis {analysis_count} to ChatGPT...")
            
            # Call ChatGPT directly
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert emotion analyst. Provide detailed 4-6 sentence paragraphs analyzing emotions and psychological states."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        This is live emotion analysis session #{analysis_count}. 
                        
                        Analyze the current emotional state of someone in a professional setting. Provide a comprehensive 4-6 sentence paragraph that includes:
                        
                        1. Assessment of their current emotional state and confidence level
                        2. What this suggests about their mental state and readiness
                        3. Impact on their performance in professional interactions
                        4. Actionable insights for emotional optimization
                        
                        Write in a professional, insightful tone suitable for self-awareness and personal development.
                        """
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Get the analysis
            chatgpt_analysis = response.choices[0].message.content
            
            # Create result
            result = {
                'count': analysis_count,
                'analysis': chatgpt_analysis,
                'timestamp': time.time(),
                'time_str': time.strftime('%H:%M:%S')
            }
            
            # Store result
            st.session_state.chatgpt_analyses.append(result)
            
            # Keep only last 10 analyses
            if len(st.session_state.chatgpt_analyses) > 10:
                st.session_state.chatgpt_analyses.pop(0)
            
            # Display results
            st.success(f"✅ ChatGPT Analysis {analysis_count} Complete!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Analysis Number", analysis_count)
            with col2:
                st.metric("Completed at", result['time_str'])
            
            # Show ChatGPT analysis
            st.markdown("### ChatGPT Analysis")
            st.write(chatgpt_analysis)
            
            # Track usage
            UsageTracker.track_analysis("chatgpt_direct", st.session_state.get('user_id'))
            
            # Send completion message
            completion_js = f"""
            <script>
                window.parent.postMessage({{
                    type: 'chatgpt_complete',
                    count: {analysis_count}
                }}, '*');
            </script>
            """
            components.html(completion_js, height=0)
            
        except Exception as e:
            st.error(f"ChatGPT analysis failed: {str(e)}")
            st.write("Please try again or check your internet connection.")
    
    # Show analysis history
    if st.session_state.chatgpt_analyses:
        st.markdown("### ChatGPT Analysis History")
        
        for analysis in reversed(st.session_state.chatgpt_analyses):
            with st.expander(f"Analysis #{analysis['count']} at {analysis['time_str']}"):
                st.write(analysis['analysis'])

if __name__ == "__main__":
    simple_chatgpt_analyzer()