import React from 'react';
import { MessageCircle, Upload, Target } from 'lucide-react';

const Navigation = ({ currentView, setCurrentView }) => {
  const tabs = [
    { id: 'chat', label: 'Chat Interface', icon: MessageCircle },
    { id: 'upload', label: 'Upload & Analyze', icon: Upload },
    { id: 'landmarks', label: 'Landmarks Tracker', icon: Target }
  ];

  return (
    <nav className="bg-gray-50 border-b">
      <div className="container mx-auto px-4">
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentView(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-colors ${
                  currentView === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;