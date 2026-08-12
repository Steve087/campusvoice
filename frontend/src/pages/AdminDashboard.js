import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import API from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function ViewAll({ sessionLike }) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [loaded, setLoaded] = useState(false);

  const load = async () => {
    if (loaded) { setOpen(!open); return; }
    try {
      const res = await API.get('/admin/all-feedback');
      setItems(res.data);
      setLoaded(true);
      setOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ marginTop: 16 }}>
      <button
        onClick={load}
        style={{
          background: 'transparent',
          border: '1px solid #2a3f6f',
          color: '#8899bb',
          padding: '8px 16px',
          borderRadius: 8,
          cursor: 'pointer',
          fontSize: 13
        }}
      >
        {open ? 'Hide All Feedback' : 'View All Feedback'}
      </button>

      {open && items.length > 0 && (
        <div style={{ marginTop: 16, overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2a3f6f' }}>
                {['#', 'Department', 'Category', 'Feedback'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: '#8899bb' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #1a2a40' }}>
                  <td style={{ padding: '8px 12px', color: '#8899bb' }}>{i + 1}</td>
                  <td style={{ padding: '8px 12px' }}>{item.department || '—'}</td>
                  <td style={{ padding: '8px 12px' }}>{item.subject || '—'}</td>
                  <td style={{ padding: '8px 12px' }}>{item.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState('');
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [submissions, setSubmissions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Auto-analyze student submissions on load
  useEffect(() => {
    const fetchSubmissions = async () => {
      try {
        const res = await API.get('/admin/submissions/analyze');
        setSubmissions(res.data);
      } catch (err) {
        console.error('Could not load submissions');
      }
    };
    fetchSubmissions();
  }, []);

  const handleUpload = async () => {
    if (!file) { setError('Select a CSV file first'); return; }
    setError(''); setLoading(true); setResult(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await API.post('/upload/', form);
      setSessionId(res.data.session_id);
      setStatus(`✓ Uploaded ${res.data.total_rows} rows. Departments: ${res.data.departments.join(', ')}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    if (!sessionId) { setError('Upload a file first'); return; }
    setError(''); setLoading(true);
    try {
      const res = await API.post('/analyze/', { session_id: sessionId, min_cluster_size: 2 });
      setResult(res.data);
      setStatus(`✓ Analysis complete — ${res.data.total_clusters} clusters found`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    }
    setLoading(false);
  };

  const renderAnalysis = (data, title) => {
    if (!data || data.total_feedback === 0) return null;
    const deptData = Object.entries(data.department_sentiments).map(([dept, score]) => ({ dept, score }));

    return (
      <div style={{ marginBottom: 40 }}>
        <h3 style={{ marginBottom: 16, color: '#00d4aa' }}>{title}</h3>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
          {[
            { label: 'Total Feedback', value: data.total_feedback },
            { label: 'Clusters Found', value: data.total_clusters },
            { label: 'Urgent Items', value: data.urgent_items.length },
          ].map(s => (
            <div className="card" key={s.label} style={{ textAlign: 'center', margin: 0 }}>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#00d4aa' }}>{s.value}</div>
              <div className="label" style={{ marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Department Sentiment Chart */}
        {deptData.length > 0 && (
          <div className="card">
            <div style={{ fontWeight: 600, marginBottom: 16 }}>Department Sentiment</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={deptData}>
                <XAxis dataKey="dept" stroke="#8899bb" />
                <YAxis stroke="#8899bb" domain={[-1, 1]} />
                <Tooltip contentStyle={{ background: '#1e2d4a', border: '1px solid #2a3f6f' }} />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {deptData.map((entry, i) => (
                    <Cell key={i} fill={entry.score < 0 ? '#ef4444' : '#00d4aa'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Clusters */}
        {data.clusters.length > 0 && (
          <div>
            <div style={{ fontWeight: 600, marginBottom: 12 }}>Clusters</div>
            {data.clusters.map((cluster, i) => (
              <div key={i} className={`card ${cluster.is_urgent ? 'urgent' : ''}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 600 }}>{cluster.label}</span>
                  <span style={{ color: cluster.sentiment_score < 0 ? '#ef4444' : '#00d4aa', fontSize: 13 }}>
                    {cluster.sentiment_score.toFixed(2)} · {cluster.size} items
                  </span>
                </div>
                {cluster.items.map((item, j) => (
                  <div key={j} style={{ fontSize: 13, color: '#8899bb', marginTop: 4 }}>• {item.text}</div>
                ))}
              </div>
            ))}
          </div>
        )}

        {/* Urgent Items */}
        {data.urgent_items.length > 0 && (
          <div>
            <div style={{ fontWeight: 600, marginBottom: 12, color: '#ef4444' }}>🚨 Urgent Items</div>
            {data.urgent_items.map((item, i) => (
              <div key={i} className="card urgent">
                <div style={{ fontSize: 13 }}>{item.text}</div>
                {item.department && <div className="label" style={{ marginTop: 4 }}>{item.department}</div>}
              </div>
            ))}
          </div>
        )}

        {/* Uncategorized / Noise */}
        {data.noise_items && data.noise_items.length > 0 && (
          <div>
            <div style={{ fontWeight: 600, marginBottom: 12, color: '#8899bb' }}>
              Uncategorized ({data.noise_items.length} items)
            </div>
            {data.noise_items.map((item, i) => (
              <div key={i} className="card" style={{ borderLeft: '4px solid #2a3f6f' }}>
                <div style={{ fontSize: 13 }}>{item.text}</div>
                {item.department && (
                  <div className="label" style={{ marginTop: 4 }}>{item.department}</div>
                )}
              </div>
            ))}
          </div>
        )}
        {/* View All Toggle */}
        <ViewAll sessionLike={title} />
      </div>
    );
  };

  return (
    <div>
      <Navbar role="admin" />
      <div style={{ maxWidth: 900, margin: '40px auto', padding: '0 24px' }}>
        <h2 style={{ marginBottom: 24 }}>Feedback Analysis</h2>

        {/* Student Submissions — auto loaded */}
        {submissions && submissions.total_feedback > 0
          ? renderAnalysis(submissions, `All Feedback (${submissions.total_feedback} total)`)
          : <div className="card" style={{ color: '#8899bb', fontSize: 13 }}>
              No student submissions yet.
            </div>
        }

        {/* CSV Upload */}
        <div className="card" style={{ marginTop: 32 }}>
          <div style={{ fontWeight: 600, marginBottom: 16 }}>Bulk CSV Upload</div>
          <div className="label">Step 1 — Upload CSV</div>
          <div style={{ display: 'flex', gap: 12, marginTop: 8, alignItems: 'center' }}>
            <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} style={{ flex: 1 }} />
            <button className="btn-primary" onClick={handleUpload} disabled={loading}>Upload</button>
          </div>
        </div>

        {sessionId && (
          <div className="card">
            <div className="label">Step 2 — Analyze</div>
            <button className="btn-primary" onClick={handleAnalyze} disabled={loading} style={{ marginTop: 8 }}>
              Analyze Feedback
            </button>
          </div>
        )}

        {status && <div style={{ color: '#00d4aa', fontSize: 13, marginBottom: 16 }}>{status}</div>}
        {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
        {loading && <div style={{ color: '#8899bb', fontSize: 13, marginBottom: 16 }}>Processing...</div>}

        {result && renderAnalysis(result, 'CSV Analysis')}
      </div>
    </div>
  );
}