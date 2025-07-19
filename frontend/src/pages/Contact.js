import React, { useState } from 'react';

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, this would send the data to the server
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h1>✅ Message Sent!</h1>
          <p>Thank you for contacting us. We'll get back to you within 24 hours.</p>
          <button 
            className="btn" 
            onClick={() => {
              setSubmitted(false);
              setFormData({ name: '', email: '', subject: '', message: '' });
            }}
          >
            Send Another Message
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h1>📞 Contact Us</h1>
        <p>Have questions? We're here to help!</p>

        <div className="grid" style={{ marginBottom: '30px' }}>
          <div className="result">
            <h3>📧 Email Support</h3>
            <p>support@emoticon.ai</p>
            <p>We typically respond within 24 hours</p>
          </div>

          <div className="result">
            <h3>💬 Live Chat</h3>
            <p>Available Monday - Friday</p>
            <p>9 AM - 6 PM EST</p>
            <button className="btn btn-secondary">
              Start Chat (Coming Soon)
            </button>
          </div>

          <div className="result">
            <h3>📚 Documentation</h3>
            <p>Find answers in our help center</p>
            <button className="btn btn-secondary">
              View Help Center (Coming Soon)
            </button>
          </div>

          <div className="result">
            <h3>🐛 Bug Reports</h3>
            <p>Found an issue? Let us know!</p>
            <p>Include steps to reproduce the problem</p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Subject *
            </label>
            <select
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            >
              <option value="">Select a subject</option>
              <option value="general">General Question</option>
              <option value="technical">Technical Support</option>
              <option value="billing">Billing Question</option>
              <option value="feature">Feature Request</option>
              <option value="bug">Bug Report</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Message *
            </label>
            <textarea
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              rows="6"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px',
                resize: 'vertical'
              }}
              placeholder="Please describe your question or issue in detail..."
            />
          </div>

          <button type="submit" className="btn" style={{ width: '100%' }}>
            Send Message
          </button>
        </form>

        <div className="notification" style={{ marginTop: '30px' }}>
          <h4>🚀 Quick Tips</h4>
          <ul>
            <li>Include screenshots for technical issues</li>
            <li>Mention your browser/device for better support</li>
            <li>Check our help center for instant answers</li>
            <li>Be specific about what you were trying to do</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Contact;