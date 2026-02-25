import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { useState } from 'react';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { hubUrl, setHubUrl, isConnected, isTauri } = useAppContext();
  const [url, setUrl] = useState(hubUrl);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${url}/info`);
      if (res.ok) {
        setTestResult('✅ Verbindung erfolgreich');
      } else {
        setTestResult(`❌ Server antwortete mit ${res.status}`);
      }
    } catch {
      setTestResult('❌ Verbindung fehlgeschlagen');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    setHubUrl(url);
    setTestResult('URL gespeichert');
  };

  const menuItems = [
    { path: '/settings/commands', label: 'Befehle', icon: '🎮', desc: 'IR-Befehle verwalten' },
    { path: '/settings/macros', label: 'Makros', icon: '⚡', desc: 'Befehlssequenzen erstellen' },
    { path: '/settings/bluetooth', label: 'Bluetooth', icon: '🔵', desc: 'BLE-Geräte verwalten' },
    { path: '/settings/images', label: 'Bilder', icon: '🖼️', desc: 'Szenenbilder verwalten' },
  ];

  return (
    <div>
      {isTauri && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Hub-Verbindung</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span className={`connection-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span className="card-subtitle">{isConnected ? 'Verbunden' : 'Nicht verbunden'}</span>
          </div>
          <div className="form-group">
            <label className="form-label">Hub-URL</label>
            <input className="form-control" value={url} onChange={e => setUrl(e.target.value)} placeholder="http://192.168.1.100:8000" />
          </div>
          {testResult && <div style={{ marginBottom: 8, fontSize: '0.9rem' }}>{testResult}</div>}
          <div className="btn-group">
            <button className="btn btn-secondary" onClick={handleTest} disabled={testing}>{testing ? 'Testen...' : 'Test'}</button>
            <button className="btn btn-primary" onClick={handleSave}>Speichern</button>
          </div>
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        {menuItems.map(item => (
          <div key={item.path} className="list-item" style={{ cursor: 'pointer' }} onClick={() => navigate(item.path)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: '1.5rem' }}>{item.icon}</span>
              <div>
                <div style={{ fontWeight: 600 }}>{item.label}</div>
                <div className="card-subtitle">{item.desc}</div>
              </div>
            </div>
            <span style={{ color: 'var(--text-secondary)' }}>›</span>
          </div>
        ))}
      </div>
    </div>
  );
}
