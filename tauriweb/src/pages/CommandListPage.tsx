import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useNavigate } from 'react-router-dom';
import { Command } from '../models/command';

export default function CommandListPage() {
  const { data: commands, loading, error, reload } = useApi(() => apiClient.getCommands(), []);
  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const navigate = useNavigate();

  const getDeviceName = (id: number) => devices?.find(d => d.id === id)?.name || `Gerät ${id}`;

  const handleDelete = async (cmdId: number, name: string) => {
    if (!confirm(`Befehl "${name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteCommand(cmdId);
      reload();
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  const handleSend = async (cmdId: number) => {
    try {
      await apiClient.sendCommand(cmdId);
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  const grouped = (commands || []).reduce<Record<number, Command[]>>((acc, cmd) => {
    if (!acc[cmd.deviceId]) acc[cmd.deviceId] = [];
    acc[cmd.deviceId].push(cmd);
    return acc;
  }, {});

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Befehle</h2>
        <button className="btn btn-primary btn-sm" onClick={() => navigate('/settings/commands/create')}>+ Neu</button>
      </div>
      {commands?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎮</div>
          <p>Keine Befehle vorhanden</p>
        </div>
      )}
      {Object.entries(grouped).map(([deviceId, cmds]) => (
        <div key={deviceId} style={{ marginBottom: 16 }}>
          <div style={{ fontWeight: 700, marginBottom: 8, color: 'var(--primary)' }}>{getDeviceName(Number(deviceId))}</div>
          {cmds.map(cmd => (
            <div key={cmd.id} className="list-item">
              <div>
                <div style={{ fontWeight: 600 }}>{cmd.name}</div>
                <div className="card-subtitle">{cmd.button}</div>
              </div>
              <div className="btn-group">
                <button className="btn btn-primary btn-sm" onClick={() => handleSend(cmd.id)}>▶</button>
                <button className="btn btn-ghost btn-sm btn-icon" onClick={() => handleDelete(cmd.id, cmd.name)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
