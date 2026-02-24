import { useState, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';

export default function BluetoothDevicesPage() {
  const { data: devices, loading, error, reload } = useApi(() => apiClient.getBleDevices(), []);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [pairingStatus, setPairingStatus] = useState<string | null>(null);

  const handleAction = async (action: () => Promise<void>, key: string) => {
    setActionLoading(key);
    try {
      await action();
      reload();
    } catch (e) {
      alert(`Fehler: ${e}`);
    } finally {
      setActionLoading(null);
    }
  };

  const startPairing = useCallback(() => {
    setPairingStatus('Pairing-Modus aktiv...');
    apiClient.startPairing().catch(() => setPairingStatus('Fehler beim Starten'));
    const ws = apiClient.createPairingWebSocket(
      (data: unknown) => {
        const msg = data as { status?: string; device?: string };
        if (msg.status) setPairingStatus(msg.status);
        if (msg.device) {
          setPairingStatus(`Gerät gefunden: ${msg.device}`);
          reload();
        }
      },
      () => setPairingStatus('WebSocket Fehler')
    );
    setTimeout(() => { ws.close(); setPairingStatus(null); }, 30000);
  }, [reload]);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Bluetooth</h2>
      </div>

      <div className="btn-group" style={{ marginBottom: 16 }}>
        <button className="btn btn-secondary" onClick={() => handleAction(() => apiClient.startAdvertisement(), 'adv')}
          disabled={actionLoading === 'adv'}>
          {actionLoading === 'adv' ? '...' : '📡 Werbung starten'}
        </button>
        <button className="btn btn-primary" onClick={startPairing}>🔗 Pairing starten</button>
      </div>

      {pairingStatus && (
        <div className="card" style={{ marginBottom: 16, borderColor: 'var(--primary)' }}>
          {pairingStatus}
        </div>
      )}

      {devices?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🔵</div>
          <p>Keine Geräte gekoppelt</p>
        </div>
      )}

      {devices?.map(device => (
        <div key={device.mac} className="card">
          <div className="card-header">
            <div>
              <div className="card-title">{device.name || device.mac}</div>
              <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                {device.paired && <span className="badge badge-primary">Gekoppelt</span>}
                {device.connected && <span className="badge badge-success">Verbunden</span>}
                {!device.connected && <span className="badge badge-danger">Getrennt</span>}
              </div>
            </div>
          </div>
          <div className="card-subtitle" style={{ marginBottom: 12 }}>{device.mac}</div>
          <div className="btn-group">
            {!device.connected ? (
              <button className="btn btn-success btn-sm"
                onClick={() => handleAction(() => apiClient.connectBle(device.mac), device.mac)}
                disabled={actionLoading === device.mac}>
                {actionLoading === device.mac ? '...' : 'Verbinden'}
              </button>
            ) : (
              <button className="btn btn-secondary btn-sm"
                onClick={() => handleAction(() => apiClient.disconnectBle(), 'disconnect')}
                disabled={actionLoading === 'disconnect'}>
                Trennen
              </button>
            )}
            <button className="btn btn-danger btn-sm"
              onClick={() => {
                if (confirm(`Gerät ${device.mac} entfernen?`)) handleAction(() => apiClient.removeBleDevice(device.mac), `remove-${device.mac}`);
              }}
              disabled={actionLoading === `remove-${device.mac}`}>
              Entfernen
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
