import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { DeviceType, CommandType } from '../models/enums';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function IntegrationsPage() {
  const navigate = useNavigate();
  const { data: devices, loading, error, reload } = useApi(() => apiClient.getDevices(), []);
  const [executing, setExecuting] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  const integrationDevices =
    devices?.filter((device) =>
      device.type === DeviceType.Integration ||
      (device.commands ?? []).some((command) => command.type === CommandType.Integration)
    ) ?? [];

  const handleExecute = async (commandId: number) => {
    setExecuting(commandId);
    try {
      await apiClient.sendCommand(commandId);
    } catch (e) {
      alert(`Fehler: ${e}`);
    } finally {
      setExecuting(null);
    }
  };

  const handleDelete = async (commandId: number, name: string) => {
    if (!confirm(`Integrations-Befehl "${name}" wirklich löschen?`)) return;
    setDeleting(commandId);
    try {
      await apiClient.deleteCommand(commandId);
      reload();
    } catch (e) {
      alert(`Fehler: ${e}`);
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Integrationen</h2>
        <div className="btn-group">
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => navigate('/devices/create?type=integration')}
          >
            + Gerät
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => navigate('/settings/commands/create?type=integration')}
          >
            + Befehl
          </button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-title" style={{ marginBottom: 8 }}>Home Assistant Setup</div>
        <div className="card-subtitle" style={{ marginBottom: 8 }}>
          Stelle sicher, dass auf dem Hub die Datei <code>config/ha_credentials.json</code> mit <code>url</code> und <code>token</code> vorhanden ist.
        </div>
        <div className="card-subtitle" style={{ marginBottom: 8 }}>
          Danach Hub neu starten und Integrations-Befehle mit gültiger Entity (z. B. <code>light.ceiling_lamp</code>) anlegen.
        </div>
      </div>

      {integrationDevices.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🔗</div>
          <p>Keine Integrationen vorhanden</p>
          <p>Lege ein Gerät vom Typ „Integration“ oder Integrations-Befehle an.</p>
          <div className="btn-group">
            <button className="btn btn-secondary" onClick={() => navigate('/devices/create?type=integration')}>
              Integrations-Gerät erstellen
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/settings/commands/create?type=integration')}>
              Integrations-Befehl erstellen
            </button>
          </div>
        </div>
      )}

      {integrationDevices.map((device) => {
        const commands = (device.commands ?? []).filter(
          (command) => command.type === CommandType.Integration
        );

        return (
          <div key={device.id} className="card" style={{ marginBottom: 12 }}>
            <div className="card-header">
              <div>
                <div className="card-title">{device.name}</div>
                <div className="card-subtitle">
                  {device.manufacturer ?? ''}
                  {device.manufacturer && device.model ? ' • ' : ''}
                  {device.model ?? ''}
                </div>
              </div>
              <div className="btn-group">
                <span className="badge badge-primary">Integration</span>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => navigate(`/settings/commands/create?type=integration&deviceId=${device.id}`)}
                  title="Integrations-Befehl für dieses Gerät erstellen"
                >
                  +
                </button>
              </div>
            </div>

            {commands.length === 0 ? (
              <div className="card-subtitle">Keine Integrations-Befehle vorhanden</div>
            ) : (
              commands.map((command) => (
                <div key={command.id} className="list-item">
                  <div>
                    <div style={{ fontWeight: 600 }}>{command.name}</div>
                    <div className="card-subtitle">
                      {command.integration_action ?? 'integration'}
                      {command.integration_entity ? ` • ${command.integration_entity}` : ''}
                    </div>
                  </div>
                  <div className="btn-group">
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleExecute(command.id)}
                      disabled={executing === command.id}
                    >
                      {executing === command.id ? '...' : '▶'}
                    </button>
                    <button
                      className="btn btn-ghost btn-sm btn-icon"
                      onClick={() => handleDelete(command.id, command.name)}
                      disabled={deleting === command.id}
                      title="Löschen"
                    >
                      {deleting === command.id ? '...' : '🗑️'}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        );
      })}
    </div>
  );
}
