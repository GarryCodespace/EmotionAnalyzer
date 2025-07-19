import React, { useState, useRef } from 'react';
import axios from 'axios';

function ChatGPTInterface() {
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Hello! I\'m your AI emotion analysis assistant. Upload an image or ask me about facial expressions and emotions.',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleSendMessage = async () => {
    if (!inputText.trim() && !fileInputRef.current?.files[0]) return;

    const userMessage = {
      type: 'user',
      content: inputText,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // If there's an image file, analyze it
      if (fileInputRef.current?.files[0]) {
        const formData = new FormData();
        formData.append('file', fileInputRef.current.files[0]);

        const response = await axios.post('/api/analyze-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const aiResponse = {
          type: 'assistant',
          content: formatAnalysisResponse(response.data),
          timestamp: new Date().toLocaleTimeString(),
          data: response.data
        };

        setMessages(prev => [...prev, aiResponse]);
        fileInputRef.current.value = '';
      } else {
        // Handle text-only questions
        const aiResponse = {
          type: 'assistant',
          content: generateTextResponse(inputText),
          timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, aiResponse]);
      }
    } catch (error) {
      const errorResponse = {
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatAnalysisResponse = (data) => {
    if (data.error) {
      return `I encountered an issue: ${data.error}. ${data.suggestion || ''}`;
    }

    const emotion = data.emotion || 'Unknown';
    const confidence = data.confidence ? (data.confidence * 100).toFixed(0) : 'Unknown';
    const mood = data.mood || 'Unable to determine';

    return `I can see ${emotion} emotion with ${confidence}% confidence. The overall mood appears to be: ${mood}. ${generateEmotionInsight(emotion)}`;
  };

  const generateEmotionInsight = (emotion) => {
    const insights = {
      'happy': 'This suggests positive feelings and good emotional state.',
      'sad': 'This indicates some level of sadness or melancholy.',
      'angry': 'This shows signs of frustration or anger.',
      'surprised': 'This suggests an unexpected or surprising moment.',
      'fear': 'This indicates anxiety or fear response.',
      'neutral': 'This shows a calm, neutral emotional state.'
    };

    return insights[emotion?.toLowerCase()] || 'Interesting expression to analyze!';
  };

  const generateTextResponse = (text) => {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('emotion') || lowerText.includes('feeling')) {
      return 'I can help analyze emotions in images! Upload a photo and I\'ll tell you what emotions I detect, including confidence levels and mood analysis.';
    } else if (lowerText.includes('how') && lowerText.includes('work')) {
      return 'I use advanced AI vision technology to analyze facial expressions and body language. Simply upload an image, and I\'ll provide detailed emotion analysis with confidence scores.';
    } else if (lowerText.includes('accuracy') || lowerText.includes('reliable')) {
      return 'My emotion detection uses state-of-the-art AI models trained on thousands of facial expressions. Accuracy depends on image quality, lighting, and clear facial visibility.';
    } else {
      return 'I\'m specialized in emotion analysis! Ask me about emotions, upload an image for analysis, or inquire about how facial expression detection works.';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🤖 ChatGPT-Style Interface</h1>
        <p>Chat with AI for simplified emotion analysis and questions</p>

        <div style={{
          height: '500px',
          overflowY: 'auto',
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '20px',
          backgroundColor: '#f9f9f9',
          marginBottom: '20px'
        }}>
          {messages.map((message, index) => (
            <div key={index} style={{
              marginBottom: '15px',
              display: 'flex',
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: message.type === 'user' ? '#007bff' : '#e9ecef',
                color: message.type === 'user' ? 'white' : '#333'
              }}>
                <div>{message.content}</div>
                <div style={{
                  fontSize: '12px',
                  opacity: 0.7,
                  marginTop: '5px'
                }}>
                  {message.timestamp}
                </div>
                {message.data && !message.data.error && (
                  <div style={{ marginTop: '10px' }}>
                    <div className={`emotion-badge ${message.data.emotion?.toLowerCase() || 'neutral'}`}>
                      {message.data.emotion} ({((message.data.confidence || 0.8) * 100).toFixed(0)}%)
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div style={{ textAlign: 'center', color: '#666' }}>
              <p>🤖 Analyzing...</p>
            </div>
          )}
        </div>

        <div style={{
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-end'
        }}>
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            style={{ display: 'none' }}
          />
          
          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            📎
          </button>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about emotions or upload an image..."
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              resize: 'none',
              minHeight: '50px'
            }}
          />

          <button
            className="btn"
            onClick={handleSendMessage}
            disabled={isLoading || (!inputText.trim() && !fileInputRef.current?.files[0])}
          >
            Send
          </button>
        </div>

        <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
          <p><strong>Tips:</strong></p>
          <ul>
            <li>Click 📎 to upload an image for emotion analysis</li>
            <li>Ask questions about emotions and facial expressions</li>
            <li>Press Enter to send messages quickly</li>
            <li>Get detailed AI analysis with confidence scores</li>
          </ul>
        </div>

        <div className="notification">
          <h4>Sample Questions</h4>
          <ul>
            <li>"How does emotion detection work?"</li>
            <li>"What emotions can you detect?"</li>
            <li>"How accurate is the analysis?"</li>
            <li>"What makes a good photo for analysis?"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ChatGPTInterface;