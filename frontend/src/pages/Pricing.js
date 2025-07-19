import React from 'react';
import { Link } from 'react-router-dom';

function Pricing() {
  return (
    <div className="container">
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>💰 Simple Pricing</h1>
        <p>Choose the plan that fits your needs</p>
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))' }}>
        {/* Free Plan */}
        <div className="card" style={{ border: '2px solid #28a745' }}>
          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <h2>🆓 Free</h2>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#28a745' }}>
              $0
            </div>
            <p>Perfect for personal use</p>
          </div>

          <ul style={{ marginBottom: '30px' }}>
            <li>✓ Unlimited image emotion analysis</li>
            <li>✓ Unlimited video analysis</li>
            <li>✓ Live camera features</li>
            <li>✓ ChatGPT-style interface</li>
            <li>✓ Simple landmarks tracker</li>
            <li>✓ Basic body language analysis</li>
            <li>✓ 1 lie detection per day</li>
            <li>✓ 1 stress analysis per day</li>
          </ul>

          <button className="btn" style={{ width: '100%', background: '#28a745' }}>
            Current Plan
          </button>
        </div>

        {/* Professional Plan */}
        <div className="card" style={{ border: '2px solid #007bff', position: 'relative' }}>
          <div style={{
            position: 'absolute',
            top: '-10px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#007bff',
            color: 'white',
            padding: '5px 20px',
            borderRadius: '20px',
            fontSize: '14px'
          }}>
            Most Popular
          </div>

          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <h2>⚡ Professional</h2>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#007bff' }}>
              $14.99
            </div>
            <p>per month</p>
          </div>

          <ul style={{ marginBottom: '30px' }}>
            <li>✓ Everything in Free plan</li>
            <li>✓ <strong>Unlimited lie detection</strong></li>
            <li>✓ <strong>Unlimited stress analysis</strong></li>
            <li>✓ Advanced body language analysis</li>
            <li>✓ Comprehensive psychological insights</li>
            <li>✓ Detailed analysis reports</li>
            <li>✓ Analysis history storage</li>
            <li>✓ Priority processing</li>
            <li>✓ Advanced confidence scoring</li>
            <li>✓ Export analysis data</li>
          </ul>

          <button className="btn" style={{ width: '100%' }}>
            Upgrade Now
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '40px', textAlign: 'center' }}>
        <h3>🎯 What's Included in Professional?</h3>
        <div className="grid">
          <div className="result">
            <h4>🕵️ Unlimited Lie Detection</h4>
            <p>Advanced deception analysis using micro-expressions and behavioral patterns</p>
          </div>
          <div className="result">
            <h4>😰 Unlimited Stress Analysis</h4>
            <p>Comprehensive stress level assessment with detailed psychological insights</p>
          </div>
          <div className="result">
            <h4>📊 Advanced Analytics</h4>
            <p>Detailed reports with confidence scores and psychological interpretations</p>
          </div>
          <div className="result">
            <h4>💾 Analysis History</h4>
            <p>Save and review all your analysis sessions with searchable history</p>
          </div>
        </div>
      </div>

      <div className="notification">
        <h3>❓ Frequently Asked Questions</h3>
        <div style={{ textAlign: 'left' }}>
          <h4>Can I cancel anytime?</h4>
          <p>Yes! Cancel your subscription anytime with no penalties. You'll continue to have access until the end of your billing period.</p>

          <h4>Is there a free trial?</h4>
          <p>The free plan gives you full access to core features. You can upgrade anytime to unlock unlimited premium features.</p>

          <h4>How accurate is the emotion detection?</h4>
          <p>Our AI uses state-of-the-art models with high accuracy. Results depend on image quality, lighting, and facial visibility.</p>

          <h4>Do you store my images?</h4>
          <p>Images are processed for analysis only and are not permanently stored. Your privacy is our priority.</p>

          <h4>What payment methods do you accept?</h4>
          <p>We accept all major credit cards and PayPal for secure, convenient payments.</p>
        </div>
      </div>

      <div className="card" style={{ textAlign: 'center', background: '#f8f9fa' }}>
        <h3>💡 Need Help Choosing?</h3>
        <p>Not sure which plan is right for you? Our team is here to help!</p>
        <Link to="/contact" className="btn btn-secondary">
          Contact Us
        </Link>
      </div>
    </div>
  );
}

export default Pricing;