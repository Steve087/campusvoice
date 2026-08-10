import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from '../api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError('');
    try {
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);

      const res = await API.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);

      if (res.data.role === 'admin') navigate('/admin');
      else navigate('/student');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div className="card" style={{ width: 400 }}>
        <h2 style={{ color: '#00d4aa', marginBottom: 24 }}>CampusVoice</h2>
        <div className="label">Email</div>
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@cec.ac.in"
          style={{ marginBottom: 16 }}
        />
        <div className="label">Password</div>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          style={{ marginBottom: 24 }}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
        />
        <button className="btn-primary" onClick={handleLogin} style={{ width: '100%' }}>
          Login
        </button>
        {error && <div className="error">{error}</div>}
        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 13, color: '#8899bb' }}>
          No account? <Link to="/register" style={{ color: '#00d4aa' }}>Register</Link>
        </div>
      </div>
    </div>
  );
}