import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';

export default function ConnectPage() {
  const { setHubUrl, isTauri } = useAppContext();
  const navigate = useNavigate();
  const [url, setUrl] = useState('http://192.168.1.100:8000');
  const [testing, setTesting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleTest = async () => {
    setTesting(true);
    setStatus(null);
    try {
      const res = await fetch(`${url}/info`);
      if (res.ok) {
        setStatus('✅ Verbindung erfolgreich!');
        setSuccess(true);
      } else {
        setStatus(`❌ Fehler: HTTP ${res.status}`);
        setSuccess(false);
      }
    } catch {
      setStatus('❌ Verbindung fehlgeschlagen. Prüfe die URL.');
      setSuccess(false);
    } finally {
      setTesting(false);
    }
  };

  const handleConnect = () => {
    setHubUrl(url);
    navigate('/scenes');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', alignItems: 'center', justifyContent: 'center', padding: 24, background: 'var(--bg-dark)' }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: '3rem', marginBottom: 8 }}>⚖️</div>
          <h1 style={{ fontSize: '2rem', color: 'var(--primary)', marginBottom: 4 }}>Equilibrium</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Smart Home Control Panel</p>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: 16, fontSize: '1.1rem' }}>Hub verbinden</h2>

          <div className="form-group">
            <label className="form-label">Hub-URL</label>
            <input
              className="form-control"
              type="url"
              value={url}
              onChange={e => { setUrl(e.target.value); setSuccess(false); setStatus(null); }}
              placeholder="http://192.168.1.100:8000"
            />
          </div>

          {status && (
            <div className={`${success ? '' : 'error-container'}`} style={{ marginBottom: 12, padding: success ? 0 : undefined }}>
              {status}
            </div>
          )}

          <div className="btn-group" style={{ flexDirection: 'column' }}>
            <button className="btn btn-secondary" onClick={handleTest} disabled={testing} style={{ width: '100%' }}>
              {testing ? 'Verbinden...' : '🔌 Verbindung testen'}
            </button>
            <button
              className="btn btn-primary"
              onClick={handleConnect}
              disabled={!success && isTauri}
              style={{ width: '100%' }}
            >
              Verbinden
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
