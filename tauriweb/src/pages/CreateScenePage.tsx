import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useApi } from '../hooks/useApi';

export default function CreateScenePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const { data: macros } = useApi(() => apiClient.getMacros(), []);

  const [name, setName] = useState('');
  const [deviceIds, setDeviceIds] = useState<number[]>([]);
  const [startMacroId, setStartMacroId] = useState<number | null>(null);
  const [stopMacroId, setStopMacroId] = useState<number | null>(null);
  const [bluetoothAddress, setBluetoothAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEdit) {
      apiClient.getScenes().then(scenes => {
        const scene = scenes.find(s => s.id === Number(id));
        if (scene) {
          setName(scene.name);
          const sceneWithLegacy = scene as typeof scene & {
            devices?: number[];
            startMacro?: number | null;
            stopMacro?: number | null;
          };
          const safeDeviceIds = Array.isArray(scene.device_ids)
            ? scene.device_ids
            : (Array.isArray(sceneWithLegacy.devices) ? sceneWithLegacy.devices : []);

          setDeviceIds(safeDeviceIds);
          setStartMacroId(scene.start_macro_id ?? sceneWithLegacy.startMacro ?? null);
          setStopMacroId(scene.stop_macro_id ?? sceneWithLegacy.stopMacro ?? null);
          setBluetoothAddress(scene.bluetooth_address ?? '');
        }
      });
    }
  }, [id, isEdit]);

  const toggleDevice = (deviceId: number) => {
    setDeviceIds(prev =>
      prev.includes(deviceId) ? prev.filter(d => d !== deviceId) : [...prev, deviceId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      const data = {
        name,
        device_ids: deviceIds,
        start_macro_id: startMacroId,
        stop_macro_id: stopMacroId,
        bluetooth_address: bluetoothAddress || null,
      };
      if (isEdit) {
        await apiClient.updateScene(Number(id), data);
      } else {
        await apiClient.createScene(data);
      }
      navigate('/scenes');
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
          <label className="form-label">Name</label>
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Szenenname" />
        </div>

        <div className="form-group">
          <label className="form-label">Geräte</label>
          {devices?.map(device => (
            <div key={device.id} className="list-item" style={{ cursor: 'pointer', marginBottom: 4 }} onClick={() => toggleDevice(device.id)}>
              <span>{device.name}</span>
              <input type="checkbox" readOnly checked={(deviceIds ?? []).includes(device.id)} />
            </div>
          ))}
        </div>

        <div className="form-group">
          <label className="form-label">Start-Makro</label>
          <select className="form-control" value={startMacroId ?? ''} onChange={e => setStartMacroId(e.target.value ? Number(e.target.value) : null)}>
            <option value="">Keins</option>
            {macros?.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Stop-Makro</label>
          <select className="form-control" value={stopMacroId ?? ''} onChange={e => setStopMacroId(e.target.value ? Number(e.target.value) : null)}>
            <option value="">Keins</option>
            {macros?.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Bluetooth-Adresse (optional)</label>
          <input className="form-control" value={bluetoothAddress} onChange={e => setBluetoothAddress(e.target.value)} placeholder="XX:XX:XX:XX:XX:XX" />
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Abbrechen</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Speichern...' : 'Speichern'}</button>
        </div>
      </form>
    </div>
  );
}
