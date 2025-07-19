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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve simple HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emoticon - Fast Emotion Analysis</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f8f9fa;
            }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 12px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 30px; }
            .upload-area { 
                border: 2px dashed #007bff; 
                border-radius: 8px; 
                padding: 40px; 
                text-align: center; 
                margin: 20px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-area:hover { background: #f8f9ff; }
            .upload-area.dragover { background: #e3f2fd; border-color: #0056b3; }
            input[type="file"] { display: none; }
            .btn { 
                background: #007bff; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 6px; 
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            .btn:hover { background: #0056b3; }
            .result { 
                margin-top: 20px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }
            .loading { text-align: center; color: #666; }
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎭 Emoticon</h1>
                <p>Fast AI-powered emotion analysis</p>
            </div>
            
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <h3>📷 Upload Image</h3>
                <p>Click here or drag and drop an image</p>
                <input type="file" id="fileInput" accept="image/*" onchange="uploadImage()">
            </div>
            
            <div id="result" style="display: none;"></div>
        </div>

        <script>
            // Drag and drop functionality
            const uploadArea = document.querySelector('.upload-area');
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    uploadFile(files[0]);
                }
            });

            async function uploadImage() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                if (file) {
                    uploadFile(file);
                }
            }

            async function uploadFile(file) {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading">🤖 Analyzing emotion...</div>';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/analyze-image', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (result.error) {
                        resultDiv.innerHTML = `<div class="result"><strong>Error:</strong> ${result.error}</div>`;
                    } else {
                        const emotionClass = result.emotion ? result.emotion.toLowerCase() : 'neutral';
                        const confidence = result.confidence ? (result.confidence * 100).toFixed(0) : 'Unknown';
                        
                        resultDiv.innerHTML = `
                            <div class="result">
                                <h3>Analysis Complete!</h3>
                                <div class="emotion-badge ${emotionClass}">
                                    ${result.emotion || 'Unknown'} (${confidence}% confidence)
                                </div>
                                <p><strong>Mood:</strong> ${result.mood || 'Unable to determine mood'}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="result"><strong>Error:</strong> Failed to analyze image</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-image")
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
        
        # Analyze emotion
        result = analyzer.analyze_emotion_fast(opencv_image)
        
        if "error" in result:
            return JSONResponse({"error": result["error"]})
        
        return JSONResponse({
            "emotion": result.get("emotion", "Unknown"),
            "confidence": result.get("confidence", 0.8),
            "mood": result.get("mood", "Unable to determine mood"),
            "landmarks_detected": landmarks_count
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Processing failed: {str(e)}"})

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