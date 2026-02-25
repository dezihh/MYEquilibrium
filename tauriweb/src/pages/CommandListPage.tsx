import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useNavigate } from 'react-router-dom';
import { Command } from '../models/command';
import { useState } from 'react';

export default function CommandListPage() {
  const { data: commands, loading, error, reload } = useApi(() => apiClient.getCommands(), []);
  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const navigate = useNavigate();
  const [filterDeviceId, setFilterDeviceId] = useState<string>('all');

  const getDeviceName = (id: number) => id === 0 ? 'Ohne Gerät' : devices?.find(d => d.id === id)?.name || `Gerät ${id}`;

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
    const key = cmd.device_id ?? 0;
    if (!acc[key]) acc[key] = [];
    acc[key].push(cmd);
    return acc;
  }, {});

  const filteredEntries = Object.entries(grouped).filter(
    ([deviceId]) => filterDeviceId === 'all' || deviceId === filterDeviceId
  );

  const deviceOptions = Object.keys(grouped).map((id) => ({
    id,
    name: getDeviceName(Number(id)),
  }));

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Befehle</h2>
        <div className="btn-group">
          <select
            className="filter-select"
            value={filterDeviceId}
            onChange={(e) => setFilterDeviceId(e.target.value)}
            title="Gerät filtern"
          >
            <option value="all">Alle Geräte</option>
            {deviceOptions.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/settings/commands/create')}>+ Neu</button>
        </div>
      </div>
      {commands?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎮</div>
          <p>Keine Befehle vorhanden</p>
        </div>
      )}
      {filteredEntries.map(([deviceId, cmds]) => (
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
