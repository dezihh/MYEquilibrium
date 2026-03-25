import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import RemotePanel from '../components/RemotePanel';
import { useNavigate } from 'react-router-dom';

const LS_KEY = 'eq_selected_device';

export default function DevicesPage() {
  const { data: devices, loading, error } = useApi(() => apiClient.getDevices(), []);
  const navigate = useNavigate();

  const [selectedId, setSelectedId] = useState<number | null>(() => {
    const stored = localStorage.getItem(LS_KEY);
    return stored ? Number(stored) : null;
  });

  // Auto-select first device once loaded if nothing stored yet
  useEffect(() => {
    if (!devices || devices.length === 0) return;
    if (selectedId === null || !devices.find(d => d.id === selectedId)) {
      const first = devices[0].id;
      setSelectedId(first);
      localStorage.setItem(LS_KEY, String(first));
    }
  }, [devices]);

  const handleSelect = (id: number) => {
    setSelectedId(id);
    localStorage.setItem(LS_KEY, String(id));
  };

  const selectedDevice = devices?.find(d => d.id === selectedId) ?? null;

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Geräte</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {devices && devices.length > 0 && (
            <select
              className="filter-select"
              value={selectedId ?? ''}
              onChange={e => handleSelect(Number(e.target.value))}
            >
              {devices.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          )}
          {selectedId && (
            <button
              className="btn btn-ghost btn-sm btn-icon"
              title="Gerät bearbeiten"
              onClick={() => navigate(`/devices/${selectedId}`)}
            >
              ⚙️
            </button>
          )}
        </div>
      </div>

      {devices && devices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📺</div>
          <p>Keine Geräte vorhanden</p>
          <p>Füge ein Gerät mit dem + Button hinzu</p>
        </div>
      ) : (
        <RemotePanel device={selectedDevice} />
      )}

      <button className="fab" onClick={() => navigate('/devices/create')}>+</button>
    </div>
  );
}

