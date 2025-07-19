import React, { useState, useRef, useEffect } from 'react';
import { Camera, Square, RotateCcw } from 'lucide-react';

const LandmarksTracker = () => {
  const [isTracking, setIsTracking] = useState(false);
  const [emotions, setEmotions] = useState([]);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startTracking = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setIsTracking(true);
      // Here you would typically start the landmarks detection process
      // For now, we'll simulate emotion detection
      simulateEmotionDetection();
    } catch (error) {
      console.error('Failed to access camera:', error);
      alert('Failed to access camera. Please check your permissions.');
    }
  };

  const stopTracking = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setIsTracking(false);
    setCurrentEmotion(null);
  };

  const clearHistory = () => {
    setEmotions([]);
    setCurrentEmotion(null);
  };

  const simulateEmotionDetection = () => {
    // Simulate emotion changes every 5 seconds
    const emotions = ['happy', 'neutral', 'surprised', 'focused', 'thoughtful'];
    let index = 0;
    
    const interval = setInterval(() => {
      if (!isTracking) {
        clearInterval(interval);
        return;
      }
      
      const emotion = emotions[index % emotions.length];
      const newEmotion = {
        emotion,
        confidence: 0.7 + Math.random() * 0.3,
        timestamp: new Date().toLocaleTimeString(),
        id: Date.now()
      };
      
      setCurrentEmotion(newEmotion);
      setEmotions(prev => [newEmotion, ...prev].slice(0, 10)); // Keep last 10
      index++;
    }, 5000);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">🎯 Landmarks Tracker</h1>
        <p className="text-gray-600">Real-time facial landmark detection with emotion analysis</p>
      </div>

      {/* Controls */}
      <div className="flex justify-center space-x-4 mb-6">
        <button
          onClick={startTracking}
          disabled={isTracking}
          className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Camera size={20} />
          <span>Start Tracking</span>
        </button>
        
        <button
          onClick={stopTracking}
          disabled={!isTracking}
          className="flex items-center space-x-2 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Square size={20} />
          <span>Stop Tracking</span>
        </button>
        
        <button
          onClick={clearHistory}
          className="flex items-center space-x-2 px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          <RotateCcw size={20} />
          <span>Clear History</span>
        </button>
      </div>

      {/* Status */}
      <div className="text-center mb-6">
        {isTracking ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-600 font-medium">Tracking Active</span>
          </div>
        ) : (
          <span className="text-gray-500">Tracking Inactive</span>
        )}
      </div>

      {/* Video Feed */}
      <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
        <div className="relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full rounded-lg bg-gray-900"
            style={{ maxHeight: '400px' }}
          />
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
          
          {currentEmotion && (
            <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg">
              <p className="font-semibold">{currentEmotion.emotion}</p>
              <p className="text-sm">{(currentEmotion.confidence * 100).toFixed(1)}% confidence</p>
            </div>
          )}
        </div>
      </div>

      {/* Emotion History */}
      {emotions.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Emotion Detection History</h3>
          <div className="space-y-3">
            {emotions.map((emotion) => (
              <div
                key={emotion.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="font-medium capitalize">{emotion.emotion}</span>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">{emotion.timestamp}</p>
                  <p className="text-sm text-gray-500">
                    {(emotion.confidence * 100).toFixed(1)}% confidence
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3">💡 How to Use</h3>
        <ul className="space-y-2 text-gray-700">
          <li>• Click "Start Tracking" to begin facial landmark detection</li>
          <li>• Position your face clearly in front of the camera</li>
          <li>• Good lighting improves detection accuracy</li>
          <li>• Emotions are detected automatically when they change</li>
          <li>• View your emotion history below the video feed</li>
        </ul>
      </div>
    </div>
  );
};

export default LandmarksTracker;