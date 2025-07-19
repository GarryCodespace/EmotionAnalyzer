import React, { useState, useCallback } from 'react';
import axios from 'axios';

function UploadImage() {
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

      const response = await axios.post('/api/analyze-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (error) {
      setResult({
        error: error.response?.data?.error || 'Failed to analyze image'
      });
    } finally {
      setLoading(false);
    }
  };

  const getEmotionClass = (emotion) => {
    if (!emotion) return 'neutral';
    return emotion.toLowerCase();
  };

  return (
    <div className="container">
      <div className="card">
        <h1>📷 Upload Image Analysis</h1>
        <p>Upload an image to analyze emotions and facial expressions using advanced AI</p>

        <div 
          className={`upload-area ${dragOver ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <h3>📷 Upload Image</h3>
          <p>Click here or drag and drop an image file</p>
          <p>Supported formats: JPG, PNG, GIF</p>
          <input
            type="file"
            id="fileInput"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>

        {file && (
          <div className="result">
            <h4>Selected File:</h4>
            <p>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</p>
            <button 
              className="btn"
              onClick={analyzeImage}
              disabled={loading}
            >
              {loading ? '🤖 Analyzing...' : '🔍 Analyze Emotion'}
            </button>
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>🤖 Analyzing emotion... Please wait</p>
          </div>
        )}

        {result && !loading && (
          <div className="result">
            <h3>Analysis Complete!</h3>
            {result.error ? (
              <div>
                <p><strong>Error:</strong> {result.error}</p>
                {result.suggestion && <p><em>{result.suggestion}</em></p>}
              </div>
            ) : (
              <div>
                <div className={`emotion-badge ${getEmotionClass(result.emotion)}`}>
                  {result.emotion || 'Unknown'} ({((result.confidence || 0.8) * 100).toFixed(0)}% confidence)
                </div>
                <p><strong>Mood:</strong> {result.mood || 'Unable to determine mood'}</p>
                {result.landmarks_detected && (
                  <p><strong>Facial landmarks detected:</strong> {result.landmarks_detected}</p>
                )}
              </div>
            )}
          </div>
        )}

        <div className="notification">
          <h4>💡 Tips for Better Results</h4>
          <ul>
            <li>Ensure good lighting and clear facial visibility</li>
            <li>Face the camera directly for best accuracy</li>
            <li>Avoid heavy shadows or obstructions</li>
            <li>Natural expressions work better than forced poses</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UploadImage;