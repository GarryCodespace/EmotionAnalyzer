import streamlit as st
import streamlit.components.v1 as components
from ai_vision_analyzer import AIVisionAnalyzer
import time
import base64
from PIL import Image
import io
import numpy as np

def test_screen_recorder():
    """Simple test version of screen recorder"""
    
    st.title("Test Screen Recorder")
    
    # Simple HTML component for testing
    html_code = """
    <div style="text-align: center; margin: 20px;">
        <button id="testBtn" onclick="sendTestData()" style="background: #0066cc; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">
            Send Test Data
        </button>
        <div id="status" style="margin-top: 20px; font-size: 16px;">Click button to test</div>
    </div>
    
    <script>
        function sendTestData() {
            document.getElementById('status').textContent = 'Sending test data...';
            
            // Send test data to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {
                    test_data: 'Hello from JavaScript',
                    timestamp: Date.now()
                }
            }, '*');
        }
    </script>
    """
    
    # Display component
    component_value = components.html(html_code, height=200)
    
    # Show component value
    if component_value:
        st.write("Received data:", component_value)
        
        # Try to analyze something simple
        if 'test_data' in component_value:
            st.success("✅ Component communication working!")
            
            # Test AI analyzer
            try:
                ai_vision = AIVisionAnalyzer()
                st.write("✅ AI Vision Analyzer loaded successfully")
                
                # Create a test image (simple numpy array)
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                test_image[:, :] = [128, 128, 128]  # Gray image
                
                # Test analysis
                result = ai_vision.analyze_facial_expressions(test_image)
                st.write("✅ AI analysis completed")
                st.write("Analysis result keys:", list(result.keys()))
                
            except Exception as e:
                st.error(f"❌ AI analysis failed: {str(e)}")
                
    else:
        st.write("No data received yet")

if __name__ == "__main__":
    test_screen_recorder()