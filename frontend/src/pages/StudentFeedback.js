import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import API from '../api';

const DEPARTMENTS = ['CSE', 'ECE', 'EEE', 'MCA'];
const CATEGORIES = [
  'WiFi / Internet',
  'Canteen / Food',
  'Teachers / Faculty',
  'Classroom / Lab',
  'Library',
  'Hostel',
  'Sports',
  'Other'
];

export default function StudentFeedback() {
  const [text, setText] = useState('');
  const [department, setDepartment] = useState('');
  const [category, setCategory] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setError('');
    setSuccess(false);
    if (!text.trim()) { setError('Feedback cannot be empty'); return; }
    if (!department) { setError('Please select your department'); return; }
    try {
      await API.post('/feedback/submit', {
        text,
        department,
        subject: category  // reusing subject field for category
      });
      setSuccess(true);
      setText('');
      setDepartment('');
      setCategory('');
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
          <div className="label">Department</div>
          <select
            value={department}
            onChange={e => setDepartment(e.target.value)}
            style={{ marginBottom: 16 }}
          >
            <option value="">Select department</option>
            {DEPARTMENTS.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>

          <div className="label">Category</div>
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            style={{ marginBottom: 16 }}
          >
            <option value="">Select category (optional)</option>
            {CATEGORIES.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

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
          {success && (
            <div style={{ color: '#00d4aa', marginTop: 12, fontSize: 13 }}>
              ✓ Feedback submitted successfully
            </div>
          )}
          {error && <div className="error">{error}</div>}
        </div>
      </div>
    </div>
  );
}