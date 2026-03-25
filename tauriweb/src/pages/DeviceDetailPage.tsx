import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import RemotePanel from '../components/RemotePanel';

export default function DeviceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: device, loading, error } = useApi(() => apiClient.getDevice(Number(id)), [id]);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error || !device) return <div className="error-container">Gerät nicht gefunden</div>;

  const handleDelete = async () => {
    if (!confirm(`Gerät "${device.name}" wirklich löschen?`)) return;
    try { await apiClient.deleteDevice(device.id); navigate('/devices'); }
    catch (e) { alert(`Fehler: ${e}`); }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title" style={{ fontSize: '1.3rem', marginBottom: 4 }}>{device.name}</div>
            <span className="badge badge-primary">{device.type}</span>
            {device.manufacturer && <span className="card-subtitle" style={{ marginTop: 4 }}>{device.manufacturer}{device.model ? ` – ${device.model}` : ''}</span>}
          </div>
        </div>
        <div className="btn-group" style={{ marginTop: 8 }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/devices/edit/${device.id}`)}>✏️ Bearbeiten</button>
          <button className="btn btn-danger" onClick={handleDelete}>🗑️ Löschen</button>
        </div>
      </div>

      <div className="card">
        <div className="card-title" style={{ marginBottom: 12 }}>Fernbedienung</div>
        <RemotePanel device={device} />
      </div>
    </div>
  );
}

