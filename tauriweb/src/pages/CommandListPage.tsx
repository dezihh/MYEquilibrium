import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useNavigate } from 'react-router-dom';
import { Command } from '../models/command';
import { useState } from 'react';
import {
  CommandType, CommandTypeLabel, CommandGroupTypeLabel, IntegrationActionLabel,
} from '../models/enums';

function CommandDetailPopup({ cmd, deviceName, onClose }: { cmd: Command; deviceName: string; onClose: () => void }) {
  const rows: { label: string; value: string }[] = [
    { label: 'ID',            value: String(cmd.id) },
    { label: 'Name',          value: cmd.name },
    { label: 'Gerät',         value: deviceName },
    { label: 'Typ',           value: CommandTypeLabel[cmd.type as CommandType] ?? cmd.type },
    { label: 'Gruppe',        value: CommandGroupTypeLabel[cmd.command_group as keyof typeof CommandGroupTypeLabel] ?? cmd.command_group },
    { label: 'Taste',         value: cmd.button },
  ];

  if (cmd.type === CommandType.Network) {
    if (cmd.host)   rows.push({ label: 'URL',    value: cmd.host });
    if (cmd.method) rows.push({ label: 'Methode',value: cmd.method.toUpperCase() });
    if (cmd.body)   rows.push({ label: 'Body',   value: cmd.body });
  } else if (cmd.type === CommandType.Bluetooth) {
    if (cmd.bt_action)       rows.push({ label: 'Taste',       value: cmd.bt_action });
    if (cmd.bt_media_action) rows.push({ label: 'Medientaste', value: cmd.bt_media_action });
  } else if (cmd.type === CommandType.Integration) {
    if (cmd.integration_action)
      rows.push({ label: 'Aktion',  value: IntegrationActionLabel[cmd.integration_action as keyof typeof IntegrationActionLabel] ?? cmd.integration_action });
    if (cmd.integration_entity) rows.push({ label: 'Entity',  value: cmd.integration_entity });
    if (cmd.body)               rows.push({ label: 'Daten',   value: cmd.body });
  } else if (cmd.type === CommandType.Script) {
    if (cmd.host) rows.push({ label: 'Skriptpfad', value: cmd.host });
  } else if (cmd.type === CommandType.Infrared) {
    const ir = cmd.ir_action;
    if (ir && Array.isArray(ir) && ir.length > 0) {
      rows.push({ label: 'IR-Pulse', value: `${ir.length} Werte` });
      rows.push({ label: 'IR-Code',  value: ir.join(', ') });
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{cmd.name}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <table className="modal-table">
          <tbody>
            {rows.map(r => (
              <tr key={r.label}>
                <td className="modal-table-label">{r.label}</td>
                <td className="modal-table-value">{r.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function CommandListPage() {
  const { data: commands, loading, error, reload } = useApi(() => apiClient.getCommands(), []);
  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const navigate = useNavigate();
  const [filterDeviceId, setFilterDeviceId] = useState<string>('all');
  const [detailCmd, setDetailCmd] = useState<Command | null>(null);

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
      {detailCmd && (
        <CommandDetailPopup
          cmd={detailCmd}
          deviceName={getDeviceName(detailCmd.device_id ?? 0)}
          onClose={() => setDetailCmd(null)}
        />
      )}
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
                <button className="btn btn-secondary btn-sm btn-icon" title="Details" onClick={() => setDetailCmd(cmd)}>🔍</button>
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
