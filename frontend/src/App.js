import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import ChatInterface from './components/ChatInterface';
import ImageUpload from './components/ImageUpload';
import LandmarksTracker from './components/LandmarksTracker';
import Header from './components/Header';
import Navigation from './components/Navigation';

function App() {
  const [currentView, setCurrentView] = useState('chat');

  return (
    <div className="App">
      <Header />
      <Navigation currentView={currentView} setCurrentView={setCurrentView} />
      
      <main className="container mx-auto px-4 py-8">
        {currentView === 'chat' && <ChatInterface />}
        {currentView === 'upload' && <ImageUpload />}
        {currentView === 'landmarks' && <LandmarksTracker />}
      </main>
    </div>
  );
}

export default App;