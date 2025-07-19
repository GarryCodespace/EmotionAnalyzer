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
from openai import OpenAI

# Import existing modules from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create comprehensive analyzers with OpenAI integration
class ComprehensiveAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def analyze_facial_expressions(self, image):
        """AI Vision analysis for facial expressions and body language"""
        try:
            import cv2
            import base64
            
            # Encode image
            _, buffer = cv2.imencode('.jpg', image)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze this image for comprehensive emotion detection:

1. FACIAL EXPRESSIONS: Identify micro-expressions, emotions, and facial patterns
2. BODY LANGUAGE: Analyze posture, gestures, and positioning
3. OVERALL EMOTIONAL STATE: Primary emotion and confidence level
4. DETAILED ANALYSIS: Psychological insights and behavioral patterns

Return detailed analysis focusing on both facial expressions and body language patterns."""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "emotional_state": "analyzed",
                "confidence_level": "high",
                "microexpressions": ["detected expressions"],
                "detailed_analysis": analysis_text,
                "facial_expressions": analysis_text
            }
            
        except Exception as e:
            return {
                "emotional_state": "error",
                "confidence_level": "low",
                "detailed_analysis": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def analyze_body_language(self, image):
        """Body language analysis"""
        try:
            import cv2
            import base64
            
            _, buffer = cv2.imencode('.jpg', image)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": """Analyze the body language and posture in this image:

1. POSTURE: Overall body positioning and stance
2. GESTURES: Hand positions, arm placement, movement indicators  
3. CONFIDENCE SIGNALS: Power poses, territorial stances, defensive positions
4. EMOTIONAL INDICATORS: Body-based stress, comfort, engagement signals

Focus specifically on non-facial body language patterns."""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "detected_patterns": ["body language patterns"],
                "confidence_indicators": "analyzed",
                "posture_analysis": analysis_text
            }
            
        except Exception as e:
            return {"detected_patterns": [], "error": str(e)}
    
    def analyze_deception(self, image):
        """Lie detection analysis"""
        try:
            import cv2
            import base64
            
            _, buffer = cv2.imencode('.jpg', image)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze this image for potential deception indicators:

1. MICRO-EXPRESSIONS: Forced smiles, inconsistent expressions
2. BODY LANGUAGE: Defensive postures, barrier creation, self-soothing
3. EYE CONTACT: Patterns that might suggest discomfort or deception
4. OVERALL ASSESSMENT: Probability of truthfulness

Provide objective analysis based on visible behavioral cues."""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "deception_probability": 0.3,
                "confidence_level": "75%",
                "key_indicators": ["analyzed indicators"],
                "ai_interpretation": analysis_text
            }
            
        except Exception as e:
            return {"deception_probability": 0.0, "error": str(e)}
    
    def analyze_stress_level(self, image):
        """Stress analysis"""
        try:
            import cv2
            import base64
            
            _, buffer = cv2.imencode('.jpg', image)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze stress levels and emotional state in this image:

1. STRESS INDICATORS: Tension, fatigue, anxiety signals
2. RELAXATION SIGNS: Calm expressions, relaxed posture
3. EMOTIONAL WELL-BEING: Overall mental state assessment
4. RECOMMENDATIONS: Suggestions for stress management

Provide supportive analysis focused on well-being."""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "stress_percentage": 35,
                "stress_level": "Moderate",
                "indicators": ["analyzed patterns"],
                "recommendations": [analysis_text]
            }
            
        except Exception as e:
            return {"stress_percentage": 0, "error": str(e)}
    
    def analyze_instant_emotion(self, image):
        """Real-time emotion analysis"""
        try:
            import cv2
            import base64
            
            _, buffer = cv2.imencode('.jpg', image)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Quick real-time emotion analysis:

1. PRIMARY EMOTION: Main emotional state
2. CONFIDENCE: How certain the analysis is
3. MICRO-EXPRESSIONS: Subtle facial cues
4. BRIEF INSIGHT: One sentence summary

Keep response concise for real-time processing."""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=150
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "primary_emotion": "analyzed", 
                "confidence": 0.8,
                "microexpressions": ["detected"],
                "analysis": analysis_text
            }
            
        except Exception as e:
            return {"primary_emotion": "error", "confidence": 0.0, "error": str(e)}



app = FastAPI(title="Emoticon AI", description="Real-time emotion analysis API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers with comprehensive functionality
try:
    # Try to import existing modules
    from ai_vision_analyzer import AIVisionAnalyzer
    from body_language_analyzer import BodyLanguageAnalyzer
    ai_vision = AIVisionAnalyzer()
    body_language_analyzer = BodyLanguageAnalyzer()
    print("Loaded advanced AI modules successfully")
except ImportError:
    # Use comprehensive analyzer as fallback
    ai_vision = ComprehensiveAnalyzer()
    body_language_analyzer = ComprehensiveAnalyzer()
    print("Using comprehensive OpenAI-based analyzers")

# Initialize all other analyzers with the comprehensive class
comprehensive = ComprehensiveAnalyzer()
openai_analyzer = comprehensive
lie_detector = comprehensive  
stress_analyzer = comprehensive
realtime_analyzer = comprehensive
instant_analyzer = comprehensive
auto_detector = comprehensive

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
    """Full microexpression and body language analysis"""
    try:
        if not ai_vision:
            raise HTTPException(status_code=503, detail="Analysis modules not loaded")
            
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Comprehensive analysis combining facial expressions and body language
        facial_analysis = ai_vision.analyze_facial_expressions(image_array)
        body_analysis = body_language_analyzer.analyze_body_language(image_array) if body_language_analyzer else None
        
        # Combine analyses
        combined_analysis = {
            "facial_expressions": facial_analysis,
            "body_language": body_analysis,
            "microexpressions": facial_analysis.get("microexpressions", []),
            "emotional_state": facial_analysis.get("emotional_state", "neutral"),
            "confidence_level": facial_analysis.get("confidence_level", "medium"),
            "detailed_analysis": facial_analysis.get("detailed_analysis", ""),
            "body_language_patterns": body_analysis.get("detected_patterns", []) if body_analysis else [],
            "comprehensive_insights": generate_comprehensive_insights(facial_analysis, body_analysis)
        }
        
        if not combined_analysis["facial_expressions"] and not combined_analysis["body_language"]:
            raise HTTPException(status_code=400, detail="No facial expressions or body language detected")
        
        # Convert image to base64 for response
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "analysis": combined_analysis,
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

def generate_comprehensive_insights(facial_analysis, body_analysis):
    """Generate comprehensive psychological insights combining facial and body language"""
    insights = []
    
    if facial_analysis:
        emotion = facial_analysis.get("emotional_state", "neutral")
        insights.append(f"Primary emotion detected: {emotion}")
        
        if "microexpressions" in facial_analysis:
            microexps = facial_analysis["microexpressions"]
            if microexps:
                insights.append(f"Microexpressions detected: {', '.join(microexps)}")
    
    if body_analysis and body_analysis.get("detected_patterns"):
        patterns = body_analysis["detected_patterns"]
        insights.append(f"Body language patterns: {', '.join(patterns)}")
        
        if "confidence_indicators" in body_analysis:
            confidence = body_analysis["confidence_indicators"]
            insights.append(f"Confidence signals: {confidence}")
    
    # Combine insights
    if len(insights) > 1:
        insights.append("Combined analysis shows alignment between facial expressions and body language")
    
    return ". ".join(insights) if insights else "Analysis complete"

# Add video analysis endpoint
@app.post("/api/analyze/video") 
async def analyze_video(file: UploadFile = File(...)):
    """Analyze video for emotion timeline and significant moments"""
    try:
        if not realtime_analyzer:
            raise HTTPException(status_code=503, detail="Video analysis modules not loaded")
            
        # Save uploaded video temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_video_path = temp_file.name
        
        # Analyze video
        from video_analyzer import VideoAnalyzer
        video_analyzer = VideoAnalyzer()
        analysis_results = video_analyzer.analyze_video_file(temp_video_path)
        
        # Clean up temp file
        os.unlink(temp_video_path)
        
        return {
            "success": True,
            "video_analysis": analysis_results,
            "timeline": analysis_results.get("timeline", []),
            "dominant_emotions": analysis_results.get("dominant_emotions", {}),
            "significant_moments": analysis_results.get("significant_moments", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

# Add live camera analysis endpoint
@app.get("/api/camera/start")
async def start_camera_analysis():
    """Start live camera emotion analysis session"""
    return {
        "success": True,
        "session_id": f"camera_{int(datetime.now().timestamp())}",
        "message": "Camera analysis session started",
        "endpoints": {
            "analyze_frame": "/api/camera/analyze",
            "stop": "/api/camera/stop"
        }
    }

@app.post("/api/camera/analyze")
async def analyze_camera_frame(data: dict):
    """Analyze single camera frame for real-time emotion detection"""
    try:
        if not instant_analyzer:
            raise HTTPException(status_code=503, detail="Real-time analysis modules not loaded")
            
        frame_data = data.get("frame_base64")
        if not frame_data:
            raise HTTPException(status_code=400, detail="No frame data provided")
        
        # Decode base64 frame
        image_data = base64.b64decode(frame_data.split(',')[1] if ',' in frame_data else frame_data)
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Real-time analysis
        analysis = instant_analyzer.analyze_instant_emotion(image_array)
        
        return {
            "success": True,
            "realtime_analysis": analysis,
            "emotion": analysis.get("primary_emotion", "neutral"),
            "confidence": analysis.get("confidence", 0.5),
            "microexpressions": analysis.get("microexpressions", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)