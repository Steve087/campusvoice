import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from '../api';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    setError('');
    try {
      const res = await API.post('/auth/register', { email, password, role });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);
      if (res.data.role === 'admin') navigate('/admin');
      else navigate('/student');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div className="card" style={{ width: 400 }}>
        <h2 style={{ color: '#00d4aa', marginBottom: 24 }}>Create Account</h2>
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
          style={{ marginBottom: 16 }}
        />
        <div className="label">Role</div>
        <select value={role} onChange={e => setRole(e.target.value)} style={{ marginBottom: 24 }}>
          <option value="student">Student</option>
          <option value="admin">Admin</option>
        </select>
        <button className="btn-primary" onClick={handleRegister} style={{ width: '100%' }}>
          Register
        </button>
        {error && <div className="error">{error}</div>}
        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 13, color: '#8899bb' }}>
          Have an account? <Link to="/login" style={{ color: '#00d4aa' }}>Login</Link>
        </div>
      </div>
    </div>
  );
}