import React, { useState, useCallback } from 'react';
import axios from 'axios';

function UploadVideo() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(0);

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

  const analyzeVideo = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/analyze-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percent);
        }
      });

      setResult(response.data);
    } catch (error) {
      setResult({
        error: error.response?.data?.error || 'Failed to analyze video'
      });
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🎥 Upload Video Analysis</h1>
        <p>Upload a video file to analyze emotions and expressions throughout the timeline</p>

        <div 
          className={`upload-area ${dragOver ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => document.getElementById('videoInput').click()}
        >
          <h3>🎥 Upload Video</h3>
          <p>Click here or drag and drop a video file</p>
          <p>Supported formats: MP4, AVI, MOV, MKV (Max 50MB)</p>
          <input
            type="file"
            id="videoInput"
            accept="video/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>

        {file && (
          <div className="result">
            <h4>Selected Video:</h4>
            <p><strong>Name:</strong> {file.name}</p>
            <p><strong>Size:</strong> {formatFileSize(file.size)}</p>
            <p><strong>Type:</strong> {file.type}</p>
            
            {file.size > 50 * 1024 * 1024 && (
              <div style={{ color: '#dc3545', margin: '10px 0' }}>
                ⚠️ Warning: File size exceeds 50MB limit. Processing may be slow or fail.
              </div>
            )}
            
            <button 
              className="btn"
              onClick={analyzeVideo}
              disabled={loading}
            >
              {loading ? '🤖 Processing...' : '🔍 Analyze Video'}
            </button>
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>🤖 Analyzing video... This may take a few minutes</p>
            {progress > 0 && (
              <div>
                <div style={{ 
                  width: '100%', 
                  backgroundColor: '#f0f0f0', 
                  borderRadius: '10px',
                  margin: '10px 0'
                }}>
                  <div style={{
                    width: `${progress}%`,
                    backgroundColor: '#007bff',
                    height: '20px',
                    borderRadius: '10px',
                    transition: 'width 0.3s'
                  }}></div>
                </div>
                <p>Upload Progress: {progress}%</p>
              </div>
            )}
          </div>
        )}

        {result && !loading && (
          <div className="result">
            <h3>Video Analysis Complete!</h3>
            {result.error ? (
              <div>
                <p><strong>Error:</strong> {result.error}</p>
                {result.suggestion && <p><em>{result.suggestion}</em></p>}
              </div>
            ) : (
              <div>
                <h4>📊 Analysis Summary</h4>
                {result.dominant_emotions && (
                  <div>
                    <p><strong>Dominant Emotions:</strong></p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                      {result.dominant_emotions.map((emotion, index) => (
                        <span key={index} className={`emotion-badge ${emotion.toLowerCase()}`}>
                          {emotion}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.timeline && result.timeline.length > 0 && (
                  <div style={{ marginTop: '20px' }}>
                    <h4>📈 Emotion Timeline</h4>
                    <div className="grid">
                      {result.timeline.slice(0, 10).map((moment, index) => (
                        <div key={index} className="result" style={{ padding: '15px' }}>
                          <p><strong>Time:</strong> {formatDuration(moment.timestamp)}</p>
                          <div className={`emotion-badge ${moment.emotion?.toLowerCase() || 'neutral'}`}>
                            {moment.emotion || 'Unknown'}
                          </div>
                          {moment.confidence && (
                            <p><strong>Confidence:</strong> {(moment.confidence * 100).toFixed(0)}%</p>
                          )}
                          {moment.analysis && (
                            <p><strong>Analysis:</strong> {moment.analysis}</p>
                          )}
                        </div>
                      ))}
                    </div>
                    {result.timeline.length > 10 && (
                      <p><em>Showing first 10 moments. Total: {result.timeline.length} significant moments detected.</em></p>
                    )}
                  </div>
                )}

                {result.total_frames && (
                  <p><strong>Total frames analyzed:</strong> {result.total_frames}</p>
                )}
              </div>
            )}
          </div>
        )}

        <div className="notification">
          <h4>💡 Video Analysis Tips</h4>
          <ul>
            <li>Shorter videos (under 5 minutes) process faster</li>
            <li>Good lighting and clear faces improve accuracy</li>
            <li>The system analyzes significant emotion changes</li>
            <li>Timeline shows key moments with detected emotions</li>
            <li>Large files may take several minutes to process</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UploadVideo;