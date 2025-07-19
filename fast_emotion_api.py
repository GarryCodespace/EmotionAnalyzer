"""
FastAPI backend for improved performance - lightweight emotion analysis
Alternative to Streamlit for better speed and responsiveness
"""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import base64
from io import BytesIO
import json
import re
import tempfile
from openai import OpenAI

# Initialize FastAPI app
app = FastAPI(title="Emoticon API", description="Fast emotion analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.7
)

# Initialize OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

class FastEmotionAnalyzer:
    """Lightweight emotion analyzer for better performance"""
    
    def __init__(self):
        self.face_mesh = face_mesh
        self.openai_client = openai_client
    
    def detect_face_landmarks(self, image):
        """Quick face detection"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            return len(results.multi_face_landmarks[0].landmark)
        return 0
    
    def analyze_emotion_fast(self, image):
        """Fast emotion analysis using OpenAI"""
        if not self.openai_client:
            return {"error": "OpenAI API not configured"}
        
        try:
            # Convert image to base64
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Quick analysis prompt
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze the emotion in this image quickly. Return JSON with: emotion (primary emotion), confidence (0-1), mood (brief description)."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {"error": str(e)}

# Initialize analyzer
analyzer = FastEmotionAnalyzer()

def parse_ai_analysis(ai_text):
    """Parse AI analysis response into structured data"""
    result = {}
    
    try:
        # Extract primary emotion
        emotion_match = re.search(r'PRIMARY EMOTION:\s*([^(]+)\s*\(([^%]+)%', ai_text, re.IGNORECASE)
        if emotion_match:
            result["emotion"] = emotion_match.group(1).strip()
            result["confidence"] = float(emotion_match.group(2).strip())
        
        # Extract mood
        mood_match = re.search(r'MOOD:\s*([^\n]+)', ai_text, re.IGNORECASE)
        if mood_match:
            result["mood"] = mood_match.group(1).strip()
        
        # Extract micro-expressions
        micro_expressions = []
        micro_section = re.search(r'MICRO-EXPRESSIONS DETECTED:(.*?)(?=BODY LANGUAGE|FACIAL ANALYSIS|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if micro_section:
            for line in micro_section.group(1).split('\n'):
                if '•' in line and line.strip():
                    expr = line.split('•')[1].strip()
                    micro_expressions.append(expr)
        result["micro_expressions"] = micro_expressions
        
        # Extract body language patterns
        body_language = []
        body_section = re.search(r'BODY LANGUAGE PATTERNS:(.*?)(?=FACIAL ANALYSIS|DECEPTION|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if body_section:
            for line in body_section.group(1).split('\n'):
                if '•' in line and line.strip():
                    pattern = line.split('•')[1].strip()
                    body_language.append(pattern)
        result["body_language"] = body_language
        
        # Extract facial analysis
        facial_analysis = []
        facial_section = re.search(r'FACIAL ANALYSIS:(.*?)(?=DECEPTION|STRESS|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if facial_section:
            for line in facial_section.group(1).split('\n'):
                if '•' in line and line.strip():
                    analysis = line.split('•')[1].strip()
                    facial_analysis.append(analysis)
        result["facial_analysis"] = facial_analysis
        
        # Extract deception analysis
        deception_match = re.search(r'Risk Level:\s*([^(]+)\s*\(([^%]+)%\)', ai_text, re.IGNORECASE)
        if deception_match:
            result["deception_risk"] = deception_match.group(1).strip()
            result["deception_percentage"] = float(deception_match.group(2).strip())
        
        deception_indicators = []
        deception_section = re.search(r'Indicators:\s*([^\n]+)', ai_text, re.IGNORECASE)
        if deception_section:
            indicators_text = deception_section.group(1).strip()
            if indicators_text and indicators_text.lower() not in ['none', 'no indicators']:
                deception_indicators = [indicators_text]
        result["deception_indicators"] = deception_indicators
        
        # Extract stress analysis
        stress_match = re.search(r'Stress Level:\s*([^%]+)%\s*\(([^)]+)\)', ai_text, re.IGNORECASE)
        if stress_match:
            result["stress_percentage"] = float(stress_match.group(1).strip())
            result["stress_level"] = stress_match.group(2).strip()
        
        stress_indicators = []
        stress_section = re.search(r'Signs:\s*([^\n]+)', ai_text, re.IGNORECASE)
        if stress_section:
            signs_text = stress_section.group(1).strip()
            if signs_text and signs_text.lower() not in ['none', 'no signs']:
                stress_indicators = [signs_text]
        result["stress_indicators"] = stress_indicators
        
        # Extract recommendations
        recommendations = []
        rec_section = re.search(r'RECOMMENDATIONS:(.*?)(?=AI PSYCHOLOGICAL|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if rec_section:
            for line in rec_section.group(1).split('\n'):
                if '•' in line and line.strip():
                    rec = line.split('•')[1].strip()
                    recommendations.append(rec)
        result["recommendations"] = recommendations
        
        # Extract psychological analysis
        psych_match = re.search(r'AI PSYCHOLOGICAL ANALYSIS:\s*([^\n]+(?:\n[^\n]+)*)', ai_text, re.IGNORECASE)
        if psych_match:
            result["psychological_analysis"] = psych_match.group(1).strip()
        
    except Exception as e:
        print(f"Error parsing AI analysis: {e}")
    
    return result

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve complete React-style single-page application"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Emoticon - Live AI Emotion Analysis</title>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                margin: 0;
                background: #f8f9fa;
            }
            .emotion-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                margin: 5px;
            }
            .happy { background: #28a745; }
            .sad { background: #6c757d; }
            .angry { background: #dc3545; }
            .surprised { background: #ffc107; color: #000; }
            .fear { background: #6f42c1; }
            .neutral { background: #17a2b8; }
            .upload-area {
                border: 2px dashed #007bff;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 20px 0;
            }
            .upload-area:hover { background: #f8f9ff; }
            .upload-area.dragover { background: #e3f2fd; border-color: #0056b3; }
        </style>
    </head>
    <body>
        <div id="root"></div>
        
        <script type="text/babel">
            const { useState, useRef, useCallback } = React;
            
            function Header() {
                return (
                    <header className="bg-white shadow-sm py-4 mb-8">
                        <div className="max-w-6xl mx-auto px-6 flex justify-between items-center">
                            <div>
                                <h1 className="text-4xl font-bold text-gray-800">Emoticon</h1>
                                <p className="text-gray-600">Live AI Emotion Interpretation from Micro-Expressions</p>
                            </div>
                            <nav className="flex gap-6">
                                <button className="text-blue-600 hover:text-blue-800">Upload Image</button>
                                <button className="text-blue-600 hover:text-blue-800">Upload Video</button>
                                <button className="text-blue-600 hover:text-blue-800">Live Camera</button>
                                <button className="text-blue-600 hover:text-blue-800">Pricing</button>
                            </nav>
                        </div>
                    </header>
                );
            }
            
            function UploadImageComponent() {
                const [file, setFile] = useState(null);
                const [result, setResult] = useState(null);
                const [loading, setLoading] = useState(false);
                const [dragOver, setDragOver] = useState(false);
                
                const handleDrop = useCallback((e) => {
                    e.preventDefault();
                    setDragOver(false);
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        setFile(files[0]);
                    }
                }, []);
                
                const handleDragOver = useCallback((e) => {
                    e.preventDefault();
                    setDragOver(true);
                }, []);
                
                const handleDragLeave = useCallback(() => {
                    setDragOver(false);
                }, []);
                
                const handleFileSelect = (e) => {
                    const selectedFile = e.target.files[0];
                    if (selectedFile) {
                        setFile(selectedFile);
                    }
                };
                
                const analyzeImage = async () => {
                    if (!file) return;
                    
                    setLoading(true);
                    setResult(null);
                    
                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await fetch('/api/analyze-image', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        setResult(data);
                    } catch (error) {
                        setResult({ error: 'Failed to analyze image' });
                    } finally {
                        setLoading(false);
                    }
                };
                
                return (
                    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                        <h2 className="text-2xl font-bold mb-4">📷 Upload Image Analysis</h2>
                        <p className="text-gray-600 mb-6">Upload an image to analyze emotions and facial expressions using advanced AI</p>
                        
                        <div 
                            className={`upload-area ${dragOver ? 'dragover' : ''}`}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onClick={() => document.getElementById('fileInput').click()}
                        >
                            <h3 className="text-xl mb-2">📷 Upload Image</h3>
                            <p>Click here or drag and drop an image file</p>
                            <p className="text-sm text-gray-500">Supported formats: JPG, PNG, GIF</p>
                            <input
                                type="file"
                                id="fileInput"
                                accept="image/*"
                                onChange={handleFileSelect}
                                style={{ display: 'none' }}
                            />
                        </div>
                        
                        {file && (
                            <div className="bg-gray-100 p-4 rounded-lg mb-4">
                                <h4 className="font-semibold">Selected File:</h4>
                                <p>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</p>
                                <button 
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg mt-2 hover:bg-blue-700"
                                    onClick={analyzeImage}
                                    disabled={loading}
                                >
                                    {loading ? '🤖 Analyzing...' : '🔍 Analyze Emotion'}
                                </button>
                            </div>
                        )}
                        
                        {loading && (
                            <div className="text-center py-8">
                                <p className="text-gray-600">🤖 Analyzing emotion... Please wait</p>
                            </div>
                        )}
                        
                        {result && !loading && (
                            <div className="bg-gray-100 p-4 rounded-lg border-l-4 border-blue-600">
                                <h3 className="text-xl font-semibold mb-2">Analysis Complete!</h3>
                                {result.error ? (
                                    <div>
                                        <p className="text-red-600"><strong>Error:</strong> {result.error}</p>
                                        {result.suggestion && <p className="text-gray-600"><em>{result.suggestion}</em></p>}
                                    </div>
                                ) : (
                                    <div>
                                        <div className="mb-4">
                                            <h4 className="text-lg font-semibold mb-2">🎭 Primary Emotional State</h4>
                                            <div className={`emotion-badge ${(result.emotion || 'neutral').toLowerCase()}`}>
                                                {result.emotion || 'Unknown'} ({((result.confidence || 0.8) * 100).toFixed(0)}% confidence)
                                            </div>
                                            <p className="mt-2"><strong>Mood:</strong> {result.mood || 'Unable to determine mood'}</p>
                                            {result.ai_analysis && (
                                                <p className="mt-2 text-sm text-gray-600"><strong>AI Analysis:</strong> {result.ai_analysis}</p>
                                            )}
                                        </div>
                                        
                                        {result.micro_expressions && result.micro_expressions.length > 0 && (
                                            <div className="mb-4">
                                                <h4 className="text-lg font-semibold mb-2">🔬 Micro-Expressions Detected: {result.micro_expressions_count || result.micro_expressions.length}</h4>
                                                <ul className="list-disc list-inside">
                                                    {result.micro_expressions.map((expression, index) => (
                                                        <li key={index} className="text-sm">• {expression}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        {result.body_language_patterns && result.body_language_patterns.length > 0 && (
                                            <div className="mb-4">
                                                <h4 className="text-lg font-semibold mb-2">🤝 Body Language Patterns Detected: {result.body_language_count || result.body_language_patterns.length}</h4>
                                                <ul className="list-disc list-inside">
                                                    {result.body_language_patterns.map((pattern, index) => (
                                                        <li key={index} className="text-sm">• {pattern}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        {result.facial_expressions && result.facial_expressions.length > 0 && (
                                            <div className="mb-4">
                                                <h4 className="text-lg font-semibold mb-2">😊 Facial Expressions Detected: {result.facial_expressions_count || result.facial_expressions.length}</h4>
                                                <ul className="list-disc list-inside">
                                                    {result.facial_expressions.map((expression, index) => (
                                                        <li key={index} className="text-sm">• {expression}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                            <div className="bg-gray-50 p-4 rounded-lg">
                                                <h4 className="text-lg font-semibold mb-2">🔍 Deception Analysis</h4>
                                                <p><strong>Deception Risk:</strong> {result.deception_risk || 'LOW'} ({(result.deception_percentage || 0).toFixed(1)}%) - Confidence: {result.deception_confidence || 'Low'}</p>
                                                {result.deception_indicators && result.deception_indicators.length > 0 && (
                                                    <div className="mt-2">
                                                        <p className="text-sm font-medium">Indicators:</p>
                                                        <ul className="list-disc list-inside text-sm">
                                                            {result.deception_indicators.map((indicator, index) => (
                                                                <li key={index}>• {indicator}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                            
                                            <div className="bg-gray-50 p-4 rounded-lg">
                                                <h4 className="text-lg font-semibold mb-2">😰 Stress & Anxiety Level</h4>
                                                <p><strong>Stress Level:</strong> You look {result.stress_percentage || 50}% stressed ({result.stress_level || 'Medium'})</p>
                                                {result.stress_indicators && result.stress_indicators.length > 0 && (
                                                    <div className="mt-2">
                                                        <p className="text-sm font-medium">Stress Indicators:</p>
                                                        <ul className="list-disc list-inside text-sm">
                                                            {result.stress_indicators.map((indicator, index) => (
                                                                <li key={index}>• {indicator}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                                {result.stress_recommendations && result.stress_recommendations.length > 0 && (
                                                    <div className="mt-2">
                                                        <p className="text-sm font-medium">Recommendations:</p>
                                                        <ul className="list-disc list-inside text-sm">
                                                            {result.stress_recommendations.map((rec, index) => (
                                                                <li key={index}>• {rec}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                        
                                        {result.landmarks_detected && (
                                            <p className="mt-4 text-sm text-gray-500"><strong>Technical:</strong> {result.landmarks_detected} facial landmarks detected</p>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                        
                        <div className="bg-blue-50 p-4 rounded-lg mt-6">
                            <h4 className="font-semibold text-blue-800">💡 Tips for Better Results</h4>
                            <ul className="text-blue-700 text-sm list-disc list-inside mt-2">
                                <li>Ensure good lighting and clear facial visibility</li>
                                <li>Face the camera directly for best accuracy</li>
                                <li>Avoid heavy shadows or obstructions</li>
                                <li>Natural expressions work better than forced poses</li>
                            </ul>
                        </div>
                    </div>
                );
            }
            
            function HomePage() {
                return (
                    <div className="max-w-6xl mx-auto px-6">
                        <div className="text-center py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg mb-8">
                            <h1 className="text-5xl font-bold mb-4">Emoticon</h1>
                            <p className="text-xl mb-2">Live AI Emotion Interpretation from Micro-Expressions</p>
                            <p className="mb-6">Try it now - Upload an image to experience AI emotion analysis</p>
                            <div className="space-x-4">
                                <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">
                                    Try Now
                                </button>
                                <button className="bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-800">
                                    ChatGPT Style Interface
                                </button>
                            </div>
                        </div>
                        
                        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                            <h2 className="text-2xl font-bold mb-6 text-center">AI Tools</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                                <div className="bg-gray-100 p-4 rounded-lg text-center">
                                    <div className="text-2xl mb-2">📷</div>
                                    <h4 className="font-semibold">Upload Image</h4>
                                    <button className="w-full mt-2 text-4xl text-gray-400 hover:text-blue-600">+</button>
                                </div>
                                
                                <div className="bg-gray-100 p-4 rounded-lg text-center">
                                    <div className="text-2xl mb-2">🎥</div>
                                    <h4 className="font-semibold">Upload Video</h4>
                                    <button className="w-full mt-2 text-4xl text-gray-400 hover:text-blue-600">+</button>
                                </div>
                                
                                <div className="bg-gray-100 p-4 rounded-lg text-center">
                                    <div className="text-2xl mb-2">🔍</div>
                                    <h4 className="font-semibold">AI Lie Detector</h4>
                                    <button className="w-full mt-2 text-4xl text-gray-400 hover:text-blue-600">+</button>
                                </div>
                                
                                <div className="bg-gray-100 p-4 rounded-lg text-center">
                                    <div className="text-2xl mb-2">😰</div>
                                    <h4 className="font-semibold">Stress Analyzer</h4>
                                    <button className="w-full mt-2 text-4xl text-gray-400 hover:text-blue-600">+</button>
                                </div>
                                
                                <div className="bg-gray-100 p-4 rounded-lg text-center">
                                    <div className="text-2xl mb-2">📊</div>
                                    <h4 className="font-semibold">Deception Level</h4>
                                    <button className="w-full mt-2 text-4xl text-gray-400 hover:text-blue-600">+</button>
                                </div>
                            </div>
                        </div>
                        
                        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                            <h2 className="text-2xl font-bold mb-4">Popular Use Cases</h2>
                            <p className="text-gray-600 mb-4">Describe your specific scenario for better analysis</p>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <button className="bg-blue-50 p-4 rounded-lg text-left hover:bg-blue-100">
                                    <div className="text-2xl mb-2">🎉</div>
                                    <h4 className="font-semibold">For Fun</h4>
                                    <p className="text-sm text-gray-600">Discover emotions in photos</p>
                                </button>
                                <button className="bg-blue-50 p-4 rounded-lg text-left hover:bg-blue-100">
                                    <div className="text-2xl mb-2">💼</div>
                                    <h4 className="font-semibold">Interview</h4>
                                    <p className="text-sm text-gray-600">Analyze confidence and honesty</p>
                                </button>
                                <button className="bg-blue-50 p-4 rounded-lg text-left hover:bg-blue-100">
                                    <div className="text-2xl mb-2">💕</div>
                                    <h4 className="font-semibold">Date</h4>
                                    <p className="text-sm text-gray-600">Understand emotional cues</p>
                                </button>
                                <button className="bg-blue-50 p-4 rounded-lg text-left hover:bg-blue-100">
                                    <div className="text-2xl mb-2">🔍</div>
                                    <h4 className="font-semibold">Interrogation</h4>
                                    <p className="text-sm text-gray-600">Professional deception analysis</p>
                                </button>
                            </div>
                        </div>
                        
                        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                            <h2 className="text-2xl font-bold mb-4">Describe Your Scenario</h2>
                            <p className="text-gray-600 mb-4">Tell us about your situation to get more personalized analysis:</p>
                            <textarea 
                                className="w-full p-4 border border-gray-300 rounded-lg resize-none"
                                rows="3"
                                placeholder="Example: Job interview analysis for confidence and honesty assessment..."
                            />
                            <button className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                                Apply Scenario Context
                            </button>
                        </div>
                        
                        <UploadImageComponent />
                        
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-2xl font-bold mb-4">Key Features</h2>
                            <ul className="space-y-2">
                                <li>✓ No login required - try all features immediately</li>
                                <li>✓ Advanced AI-powered emotion detection using GPT-4o</li>
                                <li>✓ Real-time facial landmark tracking with MediaPipe</li>
                                <li>✓ Support for images, videos, and live camera feeds</li>
                                <li>✓ Comprehensive body language analysis</li>
                                <li>✓ Professional lie detection and stress analysis</li>
                            </ul>
                        </div>
                    </div>
                );
            }
            
            function App() {
                return (
                    <div>
                        <Header />
                        <HomePage />
                    </div>
                );
            }
            
            ReactDOM.render(<App />, document.getElementById('root'));
        </script>
    </body>
    </html>
    """

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Fast image analysis endpoint"""
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Quick face detection check
        landmarks_count = analyzer.detect_face_landmarks(opencv_image)
        if landmarks_count == 0:
            return JSONResponse({
                "error": "No face detected in image",
                "suggestion": "Please upload an image with a clear, visible face"
            })
        
        # Get comprehensive analysis including body language and detailed insights
        from body_language_analyzer import BodyLanguageAnalyzer
        from lie_detector import LieDetector
        from stress_analyzer import StressAnalyzer
        
        try:
            # Use OpenAI Vision API for comprehensive micro-expression analysis
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Convert image to base64 for OpenAI Vision API
            _, buffer = cv2.imencode('.jpg', opencv_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Advanced micro-expression analysis prompt
            analysis_prompt = """
            Analyze this image for comprehensive emotional and behavioral insights. Provide detailed analysis in the following format:

            PRIMARY EMOTION: [emotion] ([confidence]% confidence)
            MOOD: [detailed mood description]
            
            MICRO-EXPRESSIONS DETECTED:
            • [specific micro-expression] ([confidence]%)
            • [specific micro-expression] ([confidence]%)
            • [specific micro-expression] ([confidence]%)
            
            BODY LANGUAGE PATTERNS:
            • [specific body language pattern]
            • [specific body language pattern]
            
            FACIAL ANALYSIS:
            • [detailed facial expression analysis]
            • [eye contact and gaze patterns]
            • [mouth and lip analysis]
            • [eyebrow and forehead analysis]
            
            DECEPTION INDICATORS:
            Risk Level: [LOW/MEDIUM/HIGH] ([percentage]%)
            Indicators: [specific indicators if any]
            
            STRESS INDICATORS:
            Stress Level: [percentage]% ([LOW/MEDIUM/HIGH])
            Signs: [specific stress signs]
            
            RECOMMENDATIONS:
            • [specific recommendation]
            • [specific recommendation]
            
            AI PSYCHOLOGICAL ANALYSIS:
            [Comprehensive 2-3 sentence analysis of the person's psychological state, emotions, and what their expressions suggest about their thoughts and feelings]
            """
            
            # Call OpenAI Vision API
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            ai_analysis = response.choices[0].message.content
            print(f"AI Analysis Response: {ai_analysis}")  # Debug log
            
            # Parse the AI response to extract structured data
            parsed_result = parse_ai_analysis(ai_analysis) if ai_analysis else {}
            
            # Initialize traditional analyzers as backup
            body_analyzer = BodyLanguageAnalyzer()
            lie_detector = LieDetector()
            stress_analyzer = StressAnalyzer()
            
            # Get traditional analysis for comparison/enhancement
            body_result = body_analyzer.analyze_body_language(opencv_image)
            lie_result = lie_detector.analyze_deception(opencv_image)
            stress_result = stress_analyzer.analyze_stress(opencv_image)
            
            # Combine AI analysis with traditional analysis
            comprehensive_result = {
                # Primary emotion data from AI
                "emotion": parsed_result.get("emotion", "Unknown"),
                "confidence": parsed_result.get("confidence", 85),
                "mood": parsed_result.get("mood", "Unable to determine mood"),
                "ai_analysis": parsed_result.get("psychological_analysis", ""),
                "landmarks_detected": landmarks_count,
                
                # Micro-expressions from AI
                "micro_expressions": parsed_result.get("micro_expressions", []),
                "micro_expressions_count": len(parsed_result.get("micro_expressions", [])),
                
                # Body language data (AI + traditional)
                "body_language_patterns": parsed_result.get("body_language", []) + body_result.get("patterns", [])[:3],
                "body_language_count": len(parsed_result.get("body_language", [])),
                "facial_expressions": parsed_result.get("facial_analysis", []),
                "facial_expressions_count": len(parsed_result.get("facial_analysis", [])),
                
                # Deception analysis (AI enhanced)
                "deception_risk": parsed_result.get("deception_risk", "LOW"),
                "deception_percentage": parsed_result.get("deception_percentage", 0.0),
                "deception_confidence": "High" if parsed_result.get("deception_indicators") else "Low",
                "deception_indicators": parsed_result.get("deception_indicators", []),
                
                # Stress analysis (AI enhanced)
                "stress_level": parsed_result.get("stress_level", "Medium"),
                "stress_percentage": parsed_result.get("stress_percentage", 50),
                "stress_indicators": parsed_result.get("stress_indicators", []),
                "stress_recommendations": parsed_result.get("recommendations", []),
                
                # Raw AI analysis
                "raw_ai_analysis": ai_analysis
            }
            
            return JSONResponse(comprehensive_result)
            
        except Exception as analysis_error:
            print(f"AI analysis error: {analysis_error}")
            # Fallback to basic emotion analysis if detailed analysis fails
            result = analyzer.analyze_emotion_fast(opencv_image)
            
            if result and "error" in result:
                return JSONResponse({"error": result["error"]})
            
            # Ensure we always return valid data
            return JSONResponse({
                "emotion": result.get("emotion", "Unknown") if result else "Unknown",
                "confidence": result.get("confidence", 0.8) if result else 0.8,
                "mood": result.get("mood", "Unable to determine mood") if result else "Unable to determine mood",
                "landmarks_detected": landmarks_count,
                "analysis_note": f"Basic analysis mode - AI analysis failed: {str(analysis_error)}"
            })
        
    except Exception as e:
        return JSONResponse({"error": f"Processing failed: {str(e)}"})

@app.post("/api/analyze-video")
async def analyze_video(file: UploadFile = File(...)):
    """Video analysis endpoint"""
    try:
        # Check file size (50MB limit)
        if file.size > 50 * 1024 * 1024:
            return JSONResponse({
                "error": "File size exceeds 50MB limit",
                "suggestion": "Please upload a smaller video file"
            })
        
        # Save temporary file
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process video
            cap = cv2.VideoCapture(temp_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            timeline = []
            frame_count = 0
            skip_frames = max(1, total_frames // 20)  # Analyze max 20 frames
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % skip_frames == 0:
                    # Analyze this frame
                    landmarks_count = analyzer.detect_face_landmarks(frame)
                    if landmarks_count > 0:
                        result = analyzer.analyze_emotion_fast(frame)
                        if "error" not in result:
                            timeline.append({
                                "timestamp": frame_count / fps,
                                "emotion": result.get("emotion", "Unknown"),
                                "confidence": result.get("confidence", 0.8),
                                "analysis": result.get("mood", "")
                            })
                
                frame_count += 1
            
            cap.release()
            
            # Calculate dominant emotions
            emotions = [moment["emotion"] for moment in timeline]
            dominant_emotions = list(set(emotions))[:5]  # Top 5 unique emotions
            
            return JSONResponse({
                "timeline": timeline,
                "dominant_emotions": dominant_emotions,
                "total_frames": frame_count,
                "duration": frame_count / fps if fps > 0 else 0
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return JSONResponse({"error": f"Video processing failed: {str(e)}"})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_configured": OPENAI_API_KEY is not None,
        "mediapipe_loaded": face_mesh is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)