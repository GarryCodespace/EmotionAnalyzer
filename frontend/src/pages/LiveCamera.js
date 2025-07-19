import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

function LiveCamera() {
  const webcamRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [results, setResults] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [autoCapture, setAutoCapture] = useState(true);

  const capture = useCallback(async () => {
    if (!webcamRef.current || analyzing) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    setAnalyzing(true);

    try {
      // Convert base64 to blob
      const response = await fetch(imageSrc);
      const blob = await response.blob();
      
      const formData = new FormData();
      formData.append('file', blob, 'capture.jpg');

      const apiResponse = await axios.post('/api/analyze-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const newResult = {
        ...apiResponse.data,
        timestamp: new Date().toLocaleTimeString(),
        image: imageSrc
      };

      setResults(prev => [newResult, ...prev.slice(0, 9)]); // Keep last 10 results
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  }, [analyzing]);

  const startAnalysis = () => {
    setIsActive(true);
    setResults([]);
  };

  const stopAnalysis = () => {
    setIsActive(false);
  };

  // Auto-capture every 3 seconds when active
  React.useEffect(() => {
    if (isActive && autoCapture) {
      const interval = setInterval(() => {
        capture();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isActive, autoCapture, capture]);

  return (
    <div className="container">
      <div className="card">
        <h1>📹 Live Camera Analysis</h1>
        <p>Real-time emotion detection using your webcam with AI analysis</p>

        <div className="video-container">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            width="100%"
            height="auto"
            videoConstraints={{
              width: 640,
              height: 480,
              facingMode: "user"
            }}
          />
          {analyzing && (
            <div className="video-overlay">
              🤖 Analyzing...
            </div>
          )}
        </div>

        <div style={{ margin: '20px 0', textAlign: 'center' }}>
          <button
            className={`btn ${isActive ? 'btn-secondary' : ''}`}
            onClick={isActive ? stopAnalysis : startAnalysis}
            style={{ marginRight: '10px' }}
          >
            {isActive ? '⏹️ Stop Analysis' : '🚀 Start Analysis'}
          </button>
          
          <button
            className="btn"
            onClick={capture}
            disabled={!isActive || analyzing}
            style={{ marginRight: '10px' }}
          >
            📸 Manual Capture
          </button>

          <label style={{ marginLeft: '20px' }}>
            <input
              type="checkbox"
              checked={autoCapture}
              onChange={(e) => setAutoCapture(e.target.checked)}
            />
            Auto-capture every 3 seconds
          </label>
        </div>

        {isActive && (
          <div className="notification">
            <p>🟢 Camera Active - {autoCapture ? 'Auto-capturing' : 'Manual capture mode'}</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="card">
            <h3>📊 Analysis Results</h3>
            <div className="grid">
              {results.map((result, index) => (
                <div key={index} className="result">
                  <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
                    <img 
                      src={result.image} 
                      alt="Capture" 
                      style={{ 
                        width: '80px', 
                        height: '60px', 
                        objectFit: 'cover',
                        borderRadius: '4px'
                      }} 
                    />
                    <div style={{ flex: 1 }}>
                      <p><strong>Time:</strong> {result.timestamp}</p>
                      {result.error ? (
                        <p style={{ color: '#dc3545' }}>{result.error}</p>
                      ) : (
                        <div>
                          <div className={`emotion-badge ${result.emotion?.toLowerCase() || 'neutral'}`}>
                            {result.emotion || 'Unknown'} ({((result.confidence || 0.8) * 100).toFixed(0)}%)
                          </div>
                          <p><strong>Mood:</strong> {result.mood || 'N/A'}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="notification">
          <h4>💡 Live Camera Tips</h4>
          <ul>
            <li>Ensure good lighting for better detection accuracy</li>
            <li>Position yourself clearly in front of the camera</li>
            <li>Auto-capture analyzes your expressions every 3 seconds</li>
            <li>Manual capture lets you control when to analyze</li>
            <li>Results show your most recent 10 analyses</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default LiveCamera;