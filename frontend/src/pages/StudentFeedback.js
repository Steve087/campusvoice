import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import API from '../api';

export default function StudentFeedback() {
  const [text, setText] = useState('');
  const [department, setDepartment] = useState('');
  const [subject, setSubject] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setError('');
    setSuccess(false);
    if (!text.trim()) { setError('Feedback cannot be empty'); return; }
    try {
      await API.post('/feedback/submit', { text, department, subject });
      setSuccess(true);
      setText('');
      setDepartment('');
      setSubject('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission failed');
    }
  };

  return (
    <div>
      <Navbar role="student" />
      <div style={{ maxWidth: 600, margin: '40px auto', padding: '0 24px' }}>
        <h2 style={{ marginBottom: 8 }}>Submit Feedback</h2>
        <p style={{ color: '#8899bb', fontSize: 13, marginBottom: 24 }}>
          Your feedback is completely anonymous.
        </p>

        <div className="card">
          <div className="label">Department (optional)</div>
          <input
            value={department}
            onChange={e => setDepartment(e.target.value)}
            placeholder="e.g. CSE, ECE"
            style={{ marginBottom: 16 }}
          />
          <div className="label">Subject (optional)</div>
          <input
            value={subject}
            onChange={e => setSubject(e.target.value)}
            placeholder="e.g. Data Structures"
            style={{ marginBottom: 16 }}
          />
          <div className="label">Your Feedback</div>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Share your thoughts..."
            rows={5}
            style={{ marginBottom: 24, resize: 'vertical' }}
          />
          <button className="btn-primary" onClick={handleSubmit} style={{ width: '100%' }}>
            Submit Anonymously
          </button>
          {success && <div style={{ color: '#00d4aa', marginTop: 12, fontSize: 13 }}>
            ✓ Feedback submitted successfully
          </div>}
          {error && <div className="error">{error}</div>}
        </div>
      </div>
    </div>
  );
}