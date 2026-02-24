import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { DeviceType, DeviceTypeLabel } from '../models/enums';

export default function CreateDevicePage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [name, setName] = useState('');
  const [type, setType] = useState<DeviceType>(DeviceType.Other);
  const [manufacturer, setManufacturer] = useState('');
  const [model, setModel] = useState('');
  const [bluetoothAddress, setBluetoothAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEdit) {
      apiClient.getDevice(Number(id)).then(device => {
        setName(device.name);
        setType(device.type);
        setManufacturer(device.manufacturer ?? '');
        setModel(device.model ?? '');
        setBluetoothAddress(device.bluetooth_address ?? '');
      });
      return;
    }

    const typeParam = searchParams.get('type');
    if (typeParam && Object.values(DeviceType).includes(typeParam as DeviceType)) {
      setType(typeParam as DeviceType);
    }
  }, [id, isEdit, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      const data = {
        name,
        type,
        manufacturer: manufacturer || null,
        model: model || null,
        bluetooth_address: bluetoothAddress || null,
      };
      if (isEdit) {
        await apiClient.updateDevice(Number(id), data);
      } else {
        await apiClient.createDevice(data);
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
          <label className="form-label">Name *</label>
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Gerätename" />
        </div>
        <div className="form-group">
          <label className="form-label">Typ</label>
          <select className="form-control" value={type} onChange={e => setType(e.target.value as DeviceType)}>
            {Object.values(DeviceType).map(t => (
              <option key={t} value={t}>{DeviceTypeLabel[t]}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Hersteller (optional)</label>
          <input className="form-control" value={manufacturer} onChange={e => setManufacturer(e.target.value)} placeholder="z.B. Samsung" />
        </div>
        <div className="form-group">
          <label className="form-label">Modell (optional)</label>
          <input className="form-control" value={model} onChange={e => setModel(e.target.value)} placeholder="z.B. QE55Q80C" />
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

