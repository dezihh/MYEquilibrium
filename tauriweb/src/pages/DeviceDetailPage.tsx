import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useState } from 'react';

export default function DeviceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: device, loading, error, reload } = useApi(() => apiClient.getDevice(Number(id)), [id]);
  const [sending, setSending] = useState<number | null>(null);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error || !device) return <div className="error-container">Gerät nicht gefunden</div>;

  const handleDelete = async () => {
    if (!confirm(`Gerät "${device.name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteDevice(device.id);
      navigate('/devices');
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  const handleDeleteCommand = async (cmdId: number) => {
    if (!confirm('Befehl wirklich löschen?')) return;
    try {
      await apiClient.deleteCommand(cmdId);
      reload();
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  const handleSendCommand = async (cmdId: number) => {
    setSending(cmdId);
    try {
      await apiClient.sendCommand(cmdId);
    } catch (e) { alert(`Fehler: ${e}`); }
    finally { setSending(null); }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title" style={{ fontSize: '1.3rem', marginBottom: 8 }}>{device.name}</div>
        <span className="badge badge-primary">{device.type}</span>
        <div className="btn-group" style={{ marginTop: 16 }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/devices/edit/${device.id}`)}>✏️ Bearbeiten</button>
          <button className="btn btn-danger" onClick={handleDelete}>🗑️ Löschen</button>
        </div>
      </div>

      <div className="page-header" style={{ marginTop: 16 }}>
        <h3 className="page-title" style={{ fontSize: '1.1rem' }}>Befehle ({device.commands.length})</h3>
        <button className="btn btn-primary btn-sm" onClick={() => navigate('/settings/commands/create')}>+ Befehl</button>
      </div>

      {device.commands.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎮</div>
          <p>Keine Befehle vorhanden</p>
        </div>
      )}

      {device.commands.map(cmd => (
        <div key={cmd.id} className="list-item">
          <div>
            <div style={{ fontWeight: 600 }}>{cmd.name}</div>
            <div className="card-subtitle">{cmd.button}</div>
          </div>
          <div className="btn-group">
            <button className="btn btn-primary btn-sm" onClick={() => handleSendCommand(cmd.id)} disabled={sending === cmd.id}>
              {sending === cmd.id ? '...' : '▶'}
            </button>
            <button className="btn btn-ghost btn-sm btn-icon" onClick={() => handleDeleteCommand(cmd.id)}>🗑️</button>
          </div>
        </div>
      ))}
    </div>
  );
}
