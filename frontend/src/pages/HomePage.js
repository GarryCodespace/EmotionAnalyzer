import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div>
      <section className="hero">
        <div className="container">
          <h1>Emoticon</h1>
          <p>Live AI Emotion Interpretation from Micro-Expressions</p>
          <p>Try it now - Upload an image to experience AI emotion analysis</p>
          <div>
            <Link to="/upload-image" className="btn" style={{marginRight: '10px'}}>
              Try Now
            </Link>
            <Link to="/chatgpt" className="btn btn-secondary">
              ChatGPT Style Interface
            </Link>
          </div>
        </div>
      </section>

      <div className="container">
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📷</div>
            <h3>Upload Image</h3>
            <p>Analyze emotions from photos instantly using advanced AI vision technology</p>
            <Link to="/upload-image" className="btn">Try Upload</Link>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🎥</div>
            <h3>Upload Video</h3>
            <p>Get comprehensive emotion analysis from video files with timeline insights</p>
            <Link to="/upload-video" className="btn">Try Video</Link>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📹</div>
            <h3>Live Camera</h3>
            <p>Real-time emotion detection using your webcam with instant AI feedback</p>
            <Link to="/live-camera" className="btn">Try Live</Link>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Landmarks Tracker</h3>
            <p>Optimized facial landmark detection for better performance and accuracy</p>
            <Link to="/landmarks" className="btn">Try Tracker</Link>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>ChatGPT Interface</h3>
            <p>Simplified chat-style interface for easy emotion analysis conversations</p>
            <Link to="/chatgpt" className="btn">Try ChatGPT</Link>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Fast Analysis</h3>
            <p>Lightning-fast emotion detection powered by optimized AI models</p>
            <Link to="/upload-image" className="btn">Get Started</Link>
          </div>
        </div>

        <div className="card">
          <h2>Popular Use Cases</h2>
          <div className="grid">
            <div className="notification">
              <h4>🎉 For Fun</h4>
              <p>Discover your emotions in photos and videos for entertainment</p>
            </div>
            <div className="notification">
              <h4>💼 Interview</h4>
              <p>Analyze body language and facial expressions during interviews</p>
            </div>
            <div className="notification">
              <h4>💕 Date</h4>
              <p>Understand emotional cues and connection during social interactions</p>
            </div>
            <div className="notification">
              <h4>🔍 Analysis</h4>
              <p>Professional emotion and stress analysis for various applications</p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Key Features</h2>
          <ul>
            <li>✓ No login required - try all features immediately</li>
            <li>✓ Advanced AI-powered emotion detection using GPT-4o</li>
            <li>✓ Real-time facial landmark tracking with MediaPipe</li>
            <li>✓ Multiple interface options (Standard, ChatGPT-style, FastAPI)</li>
            <li>✓ Support for images, videos, and live camera feeds</li>
            <li>✓ Comprehensive body language analysis</li>
            <li>✓ Professional lie detection and stress analysis</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default HomePage;