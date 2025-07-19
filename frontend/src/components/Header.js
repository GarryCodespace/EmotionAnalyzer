import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Header({ user, setUser }) {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          <div>
            <h1>Emoticon</h1>
            <p>Live AI Emotion Interpretation from Micro-Expressions</p>
          </div>
        </Link>
        
        <nav className="nav">
          <Link to="/upload-image">Upload Image</Link>
          <Link to="/upload-video">Upload Video</Link>
          <Link to="/live-camera">Live Camera</Link>
          <Link to="/landmarks">Landmarks</Link>
          <Link to="/chatgpt">ChatGPT Style</Link>
          <Link to="/pricing">Pricing</Link>
          <Link to="/contact">Contact</Link>
          
          {user ? (
            <div>
              <span>Welcome, {user.name}</span>
              <button 
                className="btn btn-secondary"
                onClick={() => setUser(null)}
              >
                Logout
              </button>
            </div>
          ) : (
            <button 
              className="btn"
              onClick={() => setShowLogin(true)}
            >
              Login (Optional)
            </button>
          )}
        </nav>
      </div>
      
      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Login (Optional)</h2>
            <p>Login to save your analysis history and access premium features.</p>
            <div className="login-options">
              <button className="btn">Gmail (Coming Soon)</button>
              <button className="btn">Apple (Coming Soon)</button>
              <button className="btn">Phone (Coming Soon)</button>
            </div>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowLogin(false)}
            >
              Continue Without Login
            </button>
          </div>
        </div>
      )}
    </header>
  );
}

export default Header;