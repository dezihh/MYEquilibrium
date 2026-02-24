import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { DeviceType } from '../models/enums';

const deviceTypeLabels: Record<DeviceType, string> = {
  [DeviceType.Display]: 'Display',
  [DeviceType.Amplifier]: 'Verstärker',
  [DeviceType.Player]: 'Player',
  [DeviceType.Other]: 'Sonstiges',
};

export default function CreateDevicePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [name, setName] = useState('');
  const [type, setType] = useState<DeviceType>(DeviceType.Other);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEdit) {
      apiClient.getDevice(Number(id)).then(device => {
        setName(device.name);
        setType(device.type);
      });
    }
  }, [id, isEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      if (isEdit) {
        await apiClient.updateDevice(Number(id), { name, type });
      } else {
        await apiClient.createDevice({ name, type });
      }
      navigate('/devices');
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
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Gerätename" />
        </div>
        <div className="form-group">
          <label className="form-label">Typ</label>
          <select className="form-control" value={type} onChange={e => setType(e.target.value as DeviceType)}>
            {Object.values(DeviceType).map(t => (
              <option key={t} value={t}>{deviceTypeLabels[t]}</option>
            ))}
          </select>
        </div>
        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Abbrechen</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Speichern...' : 'Speichern'}</button>
        </div>
      </form>
    </div>
  );
}
