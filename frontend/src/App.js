import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import UploadImage from './pages/UploadImage';
import UploadVideo from './pages/UploadVideo';
import LiveCamera from './pages/LiveCamera';
import SimpleLandmarks from './pages/SimpleLandmarks';
import ChatGPTInterface from './pages/ChatGPTInterface';
import Billing from './pages/Billing';
import Pricing from './pages/Pricing';
import Contact from './pages/Contact';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  return (
    <Router>
      <div className="App">
        <Header user={user} setUser={setUser} />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload-image" element={<UploadImage />} />
          <Route path="/upload-video" element={<UploadVideo />} />
          <Route path="/live-camera" element={<LiveCamera />} />
          <Route path="/landmarks" element={<SimpleLandmarks />} />
          <Route path="/chatgpt" element={<ChatGPTInterface />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;