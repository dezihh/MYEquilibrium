import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useApi } from '../hooks/useApi';
import { RemoteButton } from '../models/enums';

export default function CreateCommandPage() {
  const navigate = useNavigate();
  const { data: devices } = useApi(() => apiClient.getDevices(), []);

  const [name, setName] = useState('');
  const [button, setButton] = useState<RemoteButton>(RemoteButton.PowerOn);
  const [deviceId, setDeviceId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const [recordStatus, setRecordStatus] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const startRecording = useCallback(() => {
    setRecording(true);
    setRecordStatus('Warte auf IR-Signal...');
    const ws = apiClient.createCommandsWebSocket(
      (data: unknown) => {
        const msg = data as { code?: string; status?: string };
        if (msg.code) {
          setRecordStatus(`✅ Signal empfangen: ${msg.code}`);
        } else if (msg.status) {
          setRecordStatus(msg.status);
        }
        setRecording(false);
        ws.close();
      },
      () => {
        setRecordStatus('❌ WebSocket Fehler');
        setRecording(false);
      }
    );
    wsRef.current = ws;
  }, []);

  const stopRecording = () => {
    wsRef.current?.close();
    setRecording(false);
    setRecordStatus(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    if (!deviceId) { setError('Gerät ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      await apiClient.createCommand({ name, button, deviceId });
      navigate(-1);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <div className="error-container">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Gerät</label>
          <select className="form-control" value={deviceId ?? ''} onChange={e => setDeviceId(Number(e.target.value))}>
            <option value="">Gerät auswählen</option>
            {devices?.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Name</label>
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Befehlsname" />
        </div>
        <div className="form-group">
          <label className="form-label">Taste</label>
          <select className="form-control" value={button} onChange={e => setButton(e.target.value as RemoteButton)}>
            {Object.values(RemoteButton).map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">IR-Signal aufnehmen</label>
          {recordStatus && <div style={{ marginBottom: 8, fontSize: '0.9rem' }}>{recordStatus}</div>}
          <div className="btn-group">
            {!recording ? (
              <button type="button" className="btn btn-secondary" onClick={startRecording}>🔴 Aufnehmen</button>
            ) : (
              <button type="button" className="btn btn-danger" onClick={stopRecording}>⏹ Stopp</button>
            )}
          </div>
        </div>
        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Abbrechen</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Speichern...' : 'Speichern'}</button>
        </div>
      </form>
    </div>
  );
}
