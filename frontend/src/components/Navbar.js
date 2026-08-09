import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ role }) {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  return (
    <nav style={{
      background: '#1e2d4a',
      padding: '16px 32px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '1px solid #2a3f6f'
    }}>
      <span style={{ color: '#00d4aa', fontWeight: 700, fontSize: 18 }}>
        CampusVoice
      </span>
      <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <span style={{ color: '#8899bb', fontSize: 13 }}>{role}</span>
        <button className="btn-danger" onClick={logout} style={{ padding: '6px 14px' }}>
          Logout
        </button>
      </div>
    </nav>
  );
}