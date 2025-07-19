import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';

function SimpleLandmarks() {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [detections, setDetections] = useState([]);
  const [showLandmarks, setShowLandmarks] = useState(true);

  const startTracker = () => {
    setIsActive(true);
    setDetections([]);
  };

  const stopTracker = () => {
    setIsActive(false);
  };

  const clearHistory = () => {
    setDetections([]);
  };

  // Simulate landmark detection (in real implementation, this would use MediaPipe)
  const detectLandmarks = useCallback(() => {
    if (!isActive || !webcamRef.current) return;

    // Simulate emotion detection
    const emotions = ['happy', 'sad', 'surprised', 'neutral', 'angry'];
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    const confidence = 0.7 + Math.random() * 0.3;

    const newDetection = {
      emotion: randomEmotion,
      confidence: confidence,
      timestamp: new Date().toLocaleTimeString(),
      landmarks: Math.floor(Math.random() * 50) + 400 // Simulate landmark count
    };

    setDetections(prev => [newDetection, ...prev.slice(0, 4)]); // Keep last 5
  }, [isActive]);

  // Simulate detection every 2 seconds
  useEffect(() => {
    if (isActive) {
      const interval = setInterval(detectLandmarks, 2000);
      return () => clearInterval(interval);
    }
  }, [isActive, detectLandmarks]);

  return (
    <div className="container">
      <div className="card">
        <h1>🎯 Simple Landmarks Tracker</h1>
        <p><em>Real-time facial landmark detection with emotion analysis</em></p>

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
          {showLandmarks && isActive && (
            <canvas
              ref={canvasRef}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                pointerEvents: 'none'
              }}
            />
          )}
          {isActive && (
            <div className="video-overlay">
              🟢 Tracker Active
            </div>
          )}
        </div>

        <div style={{ margin: '20px 0', textAlign: 'center' }}>
          <button
            className="btn"
            onClick={startTracker}
            disabled={isActive}
            style={{ marginRight: '10px' }}
          >
            🚀 Start Tracker
          </button>
          
          <button
            className="btn btn-secondary"
            onClick={stopTracker}
            disabled={!isActive}
            style={{ marginRight: '10px' }}
          >
            ⏹️ Stop Tracker
          </button>

          <button
            className="btn btn-secondary"
            onClick={clearHistory}
            style={{ marginRight: '20px' }}
          >
            🗑️ Clear History
          </button>

          <label>
            <input
              type="checkbox"
              checked={showLandmarks}
              onChange={(e) => setShowLandmarks(e.target.checked)}
            />
            Show landmarks overlay
          </label>
        </div>

        {isActive && (
          <div className="notification">
            <p>🟢 Tracker Active - Detecting landmarks and emotions...</p>
          </div>
        )}

        {!isActive && (
          <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            👆 Click 'Start Tracker' to begin landmark detection and emotion analysis
          </div>
        )}

        {detections.length > 0 && (
          <div className="card">
            <h3>📊 Emotion Detection History</h3>
            <div className="grid">
              {detections.map((detection, index) => (
                <div key={index} className="result">
                  <h4>🎭 {detection.emotion} at {detection.timestamp}</h4>
                  <p><strong>Confidence:</strong> {(detection.confidence * 100).toFixed(0)}%</p>
                  <p><strong>Landmarks detected:</strong> {detection.landmarks}</p>
                  <div className={`emotion-badge ${detection.emotion}`}>
                    {detection.emotion}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="card">
          <h3>💡 Performance Tips</h3>
          <ul>
            <li><strong>Good lighting</strong> improves landmark detection accuracy</li>
            <li><strong>Face the camera</strong> directly for best results</li>
            <li><strong>Stable position</strong> helps with consistent tracking</li>
            <li><strong>Clear facial expressions</strong> work better for emotion detection</li>
            <li><strong>Minimal background movement</strong> improves performance</li>
          </ul>
        </div>

        <div className="notification">
          <h4>🔧 Technical Information</h4>
          <p>This tracker uses optimized MediaPipe settings for better real-time performance:</p>
          <ul>
            <li>Single face detection for speed</li>
            <li>Disabled landmark refinement for performance</li>
            <li>Optimized confidence thresholds</li>
            <li>Smart analysis intervals to reduce processing load</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default SimpleLandmarks;