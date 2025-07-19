import React from 'react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🎭</span>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Emoticon</h1>
              <p className="text-sm text-gray-600">AI-powered emotion analysis</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors">
              About
            </button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors">
              Contact
            </button>
            <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              Login
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;