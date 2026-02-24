import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import DeviceCard from '../components/DeviceCard';
import { useNavigate } from 'react-router-dom';

export default function DevicesPage() {
  const { data: devices, loading, error, reload } = useApi(() => apiClient.getDevices(), []);
  const navigate = useNavigate();

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Geräte</h2>
      </div>
      {devices && devices.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📺</div>
          <p>Keine Geräte vorhanden</p>
          <p>Füge ein Gerät mit dem + Button hinzu</p>
        </div>
      )}
      {devices?.map(device => (
        <DeviceCard key={device.id} device={device} onRefresh={reload} />
      ))}
      <button className="fab" onClick={() => navigate('/devices/create')}>+</button>
    </div>
  );
}
