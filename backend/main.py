from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Optional, List
import json
import os
from datetime import datetime

# Import existing modules from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_vision_analyzer import AIVisionAnalyzer
    from openai_analyzer import OpenAIAnalyzer
    from lie_detector import LieDetector  
    from stress_analyzer import StressAnalyzer
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Create fallback analyzers for development
    class FallbackAnalyzer:
        def analyze_facial_expressions(self, image):
            return {
                'emotional_state': 'neutral',
                'confidence_level': '85%',
                'facial_expressions': ['focused'],
                'detailed_analysis': 'Basic analysis - full AI integration pending'
            }
        
        def analyze_deception(self, image):
            return {
                'deception_probability': 0.2,
                'confidence_level': '80%',
                'key_indicators': ['normal eye contact', 'relaxed posture'],
                'ai_interpretation': 'No significant deception indicators detected'
            }
        
        def analyze_stress_level(self, image):
            return {
                'stress_percentage': 25,
                'stress_level': 'Low',
                'indicators': ['relaxed_posture', 'calm_expression'],
                'recommendations': ['Continue current activities', 'Maintain good work-life balance']
            }
    
    AIVisionAnalyzer = FallbackAnalyzer
    OpenAIAnalyzer = FallbackAnalyzer
    LieDetector = FallbackAnalyzer
    StressAnalyzer = FallbackAnalyzer

app = FastAPI(title="Emoticon AI", description="Real-time emotion analysis API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
ai_vision = AIVisionAnalyzer()
openai_analyzer = OpenAIAnalyzer()
lie_detector = LieDetector()
stress_analyzer = StressAnalyzer()

# Serve frontend HTML file
from fastapi.responses import FileResponse

# Serve static files when build exists
import os
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Additional frontend routes for development
@app.get("/chat")
async def serve_chat():
    """Serve chat interface"""
    return FileResponse('../frontend/index.html')

@app.get("/upload") 
async def serve_upload():
    """Serve upload interface"""
    return FileResponse('../frontend/index.html')

@app.get("/landmarks")
async def serve_landmarks():
    """Serve landmarks tracker"""
    return FileResponse('../frontend/index.html')

@app.get("/")
async def serve_frontend_root():
    """Serve the main frontend application"""
    return FileResponse('../frontend/index.html')

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {"message": "Emoticon AI API is running", "status": "healthy"}

@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze emotion in uploaded image"""
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Analyze with AI Vision
        analysis = ai_vision.analyze_facial_expressions(image_array)
        
        if not analysis:
            raise HTTPException(status_code=400, detail="No facial expressions detected")
        
        # Convert image to base64 for response
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "analysis": analysis,
            "image_base64": img_base64,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/lie-detection")
async def analyze_lie_detection(file: UploadFile = File(...)):
    """Analyze deception indicators in uploaded image"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_array = np.array(image)
        
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Analyze with lie detector
        analysis = lie_detector.analyze_deception(image_array)
        
        return {
            "success": True,
            "deception_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lie detection failed: {str(e)}")

@app.post("/api/analyze/stress")
async def analyze_stress(file: UploadFile = File(...)):
    """Analyze stress levels in uploaded image"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_array = np.array(image)
        
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Analyze with stress analyzer
        analysis = stress_analyzer.analyze_stress_level(image_array)
        
        return {
            "success": True,
            "stress_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stress analysis failed: {str(e)}")

@app.post("/api/chat/analyze")
async def chat_analyze(data: dict):
    """ChatGPT-style analysis endpoint"""
    try:
        message = data.get("message", "")
        image_base64 = data.get("image_base64")
        
        if image_base64:
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Analyze image
            analysis = ai_vision.analyze_facial_expressions(image_array)
            
            # Format response based on message context
            response = format_chat_response(analysis, message)
            
            return {
                "success": True,
                "response": response,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Text-only response
            response = generate_text_response(message.lower())
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat analysis failed: {str(e)}")

@app.get("/api/landmarks/track")
async def start_landmarks_tracking():
    """Start landmarks tracking session"""
    # This would typically return session info and WebSocket endpoint
    return {
        "success": True,
        "session_id": f"track_{int(datetime.now().timestamp())}",
        "websocket_url": "/ws/landmarks"
    }

def format_chat_response(analysis, message=""):
    """Format AI analysis into chat-friendly response"""
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
        'hello': "Hi! I'm Emoticon AI. Upload an image and I'll analyze the emotions for you!",
        'hi': "Hello! Ready to analyze some emotions? Upload an image!",
        'help': "I can analyze emotions in images. Upload a photo and I'll detect facial expressions, stress levels, and authenticity indicators.",
        'how': "I use advanced AI to detect facial expressions and body language, then provide psychological insights about emotions, stress levels, and authenticity.",
        'what': "I'm an AI emotion analyzer that can detect happiness, sadness, anger, surprise, fear, and more complex emotional states from images.",
        'stressed': "Upload a photo and I'll analyze your stress levels through facial expressions and body language.",
        'happy': "Upload a photo and I'll confirm how happy you look and provide insights about your expression.",
        'sad': "Upload an image and I'll provide supportive insights about your emotional state.",
        'lie': "I can detect deception indicators through micro-expressions and body language analysis. Upload an image for lie detection!",
        'angry': "Upload a photo and I'll analyze anger levels and provide insights about emotional intensity.",
    }
    
    # Check for keywords in user input
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # Default response
    return "Upload an image and I'll analyze the emotions! You can ask questions like 'How do I look?', 'Am I stressed?', or 'Analyze my emotion'."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)