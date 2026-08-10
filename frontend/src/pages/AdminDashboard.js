import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import API from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function AdminDashboard() {
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState('');
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

  const handleEmbed = async () => {
    if (!sessionId) { setError('Upload a file first'); return; }
    setError(''); setLoading(true);
    try {
      const res = await API.post('/embed/', { session_id: sessionId });
      setStatus(`✓ Embeddings generated: ${res.data.vectors_shape[0]} vectors`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Embedding failed');
    }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    if (!sessionId) { setError('Upload and embed first'); return; }
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

  const deptData = result
    ? Object.entries(result.department_sentiments).map(([dept, score]) => ({ dept, score }))
    : [];

  return (
    <div>
      <Navbar role="admin" />
      <div style={{ maxWidth: 900, margin: '40px auto', padding: '0 24px' }}>
        <h2 style={{ marginBottom: 24 }}>Feedback Analysis</h2>

        {/* Upload Section */}
        <div className="card">
          <div className="label">Step 1 — Upload CSV</div>
          <div style={{ display: 'flex', gap: 12, marginTop: 8, alignItems: 'center' }}>
            <input
              type="file"
              accept=".csv"
              onChange={e => setFile(e.target.files[0])}
              style={{ flex: 1 }}
            />
            <button className="btn-primary" onClick={handleUpload} disabled={loading}>
              Upload
            </button>
          </div>
        </div>

        {/* Pipeline Buttons */}
        {sessionId && (
          <div className="card">
            <div className="label">Step 2 — Run Pipeline</div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
              <button className="btn-primary" onClick={handleEmbed} disabled={loading}>
                Generate Embeddings
              </button>
              <button className="btn-primary" onClick={handleAnalyze} disabled={loading}>
                Analyze
              </button>
            </div>
          </div>
        )}

        {/* Status */}
        {status && (
          <div style={{ color: '#00d4aa', fontSize: 13, marginBottom: 16 }}>{status}</div>
        )}
        {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
        {loading && <div style={{ color: '#8899bb', fontSize: 13, marginBottom: 16 }}>Processing...</div>}

        {/* Results */}
        {result && (
          <>
            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
              {[
                { label: 'Total Feedback', value: result.total_feedback },
                { label: 'Clusters Found', value: result.total_clusters },
                { label: 'Urgent Items', value: result.urgent_items.length },
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
                    <Tooltip
                      contentStyle={{ background: '#1e2d4a', border: '1px solid #2a3f6f' }}
                    />
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
            {result.clusters.length > 0 && (
              <div>
                <div style={{ fontWeight: 600, marginBottom: 12 }}>Feedback Clusters</div>
                {result.clusters.map(cluster => (
                  <div key={cluster.cluster_id} className={`card ${cluster.is_urgent ? 'urgent' : ''}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontWeight: 600 }}>{cluster.label}</span>
                      <span style={{ color: cluster.sentiment_score < 0 ? '#ef4444' : '#00d4aa', fontSize: 13 }}>
                        {cluster.sentiment_score.toFixed(2)} · {cluster.size} items
                      </span>
                    </div>
                    {cluster.items.map(item => (
                      <div key={item.id} style={{ fontSize: 13, color: '#8899bb', marginTop: 4 }}>
                        • {item.text}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}

            {/* Urgent Items */}
            {result.urgent_items.length > 0 && (
              <div>
                <div style={{ fontWeight: 600, marginBottom: 12, color: '#ef4444' }}>
                  🚨 Urgent Items
                </div>
                {result.urgent_items.map((item, i) => (
                  <div key={i} className="card urgent">
                    <div style={{ fontSize: 13 }}>{item.text}</div>
                    {item.department && (
                      <div className="label" style={{ marginTop: 4 }}>{item.department}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}