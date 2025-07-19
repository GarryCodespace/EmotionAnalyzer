import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Billing() {
  const [activeTab, setActiveTab] = useState('current');

  return (
    <div className="container">
      <div className="card">
        <h1>💳 Billing & Usage</h1>
        <p>Manage your subscription and view usage statistics</p>

        <div style={{ borderBottom: '1px solid #ddd', marginBottom: '20px' }}>
          <button
            className={`btn ${activeTab === 'current' ? '' : 'btn-secondary'}`}
            onClick={() => setActiveTab('current')}
            style={{ marginRight: '10px', marginBottom: '10px' }}
          >
            Current Plan
          </button>
          <button
            className={`btn ${activeTab === 'usage' ? '' : 'btn-secondary'}`}
            onClick={() => setActiveTab('usage')}
            style={{ marginRight: '10px', marginBottom: '10px' }}
          >
            Usage Stats
          </button>
          <button
            className={`btn ${activeTab === 'history' ? '' : 'btn-secondary'}`}
            onClick={() => setActiveTab('history')}
            style={{ marginBottom: '10px' }}
          >
            Billing History
          </button>
        </div>

        {activeTab === 'current' && (
          <div>
            <div className="notification">
              <h3>🆓 Free Plan</h3>
              <p>You're currently on the free plan with the following benefits:</p>
              <ul>
                <li>✓ Unlimited image emotion analysis</li>
                <li>✓ Unlimited video analysis</li>
                <li>✓ Live camera features</li>
                <li>✓ ChatGPT-style interface</li>
                <li>✓ 1 lie detection per day</li>
                <li>✓ 1 stress analysis per day</li>
              </ul>
            </div>

            <div className="card" style={{ background: '#f8f9fa', margin: '20px 0' }}>
              <h4>⚡ Professional Plan - $14.99/month</h4>
              <ul>
                <li>✓ Everything in Free plan</li>
                <li>✓ Unlimited lie detection</li>
                <li>✓ Unlimited stress analysis</li>
                <li>✓ Advanced body language analysis</li>
                <li>✓ Priority processing</li>
                <li>✓ Detailed analysis reports</li>
                <li>✓ Analysis history storage</li>
              </ul>
              <Link to="/pricing" className="btn">
                Upgrade to Professional
              </Link>
            </div>

            <div className="result">
              <h4>💡 Need Help?</h4>
              <p>Contact our support team for billing questions or account assistance.</p>
              <Link to="/contact" className="btn btn-secondary">
                Contact Support
              </Link>
            </div>
          </div>
        )}

        {activeTab === 'usage' && (
          <div>
            <h3>📊 Usage Statistics</h3>
            
            <div className="grid">
              <div className="result">
                <h4>Today's Usage</h4>
                <p><strong>Image Analysis:</strong> 0 / Unlimited</p>
                <p><strong>Video Analysis:</strong> 0 / Unlimited</p>
                <p><strong>Lie Detection:</strong> 0 / 1</p>
                <p><strong>Stress Analysis:</strong> 0 / 1</p>
              </div>

              <div className="result">
                <h4>This Month</h4>
                <p><strong>Total Analyses:</strong> 0</p>
                <p><strong>Premium Features:</strong> 0</p>
                <p><strong>Processing Time:</strong> 0 minutes</p>
              </div>
            </div>

            <div className="notification">
              <h4>📈 Upgrade Benefits</h4>
              <p>Professional plan users get unlimited access to all premium features plus detailed usage analytics.</p>
              <Link to="/pricing" className="btn">
                View Pricing
              </Link>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <h3>🧾 Billing History</h3>
            
            <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
              <p>No billing history available.</p>
              <p>You're currently on the free plan.</p>
              <Link to="/pricing" className="btn">
                View Paid Plans
              </Link>
            </div>
          </div>
        )}

        <div className="card" style={{ marginTop: '30px', background: '#e3f2fd' }}>
          <h4>💰 Transparent Pricing</h4>
          <ul>
            <li>No hidden fees or surprise charges</li>
            <li>Cancel anytime with no penalties</li>
            <li>Free plan always available</li>
            <li>30-day money-back guarantee on paid plans</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Billing;