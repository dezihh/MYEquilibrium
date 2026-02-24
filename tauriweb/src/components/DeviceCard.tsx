import { Device } from '../models/device';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/apiClient';

interface Props {
  device: Device;
  onRefresh: () => void;
}

const typeLabels: Record<string, string> = {
  display: 'Display',
  amplifier: 'Verstärker',
  player: 'Player',
  other: 'Sonstiges',
};

export default function DeviceCard({ device, onRefresh }: Props) {
  const navigate = useNavigate();

  const handleDelete = async () => {
    if (!confirm(`Gerät "${device.name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteDevice(device.id);
      onRefresh();
    } catch (e) {
      alert(`Fehler: ${e}`);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <div className="card-title">{device.name}</div>
          <span className="badge badge-primary">
            <span className={`device-type-${device.type}`}></span> {typeLabels[device.type] || device.type}
          </span>
        </div>
        <div className="btn-group">
          <button className="btn btn-ghost btn-sm btn-icon" onClick={() => navigate(`/devices/${device.id}`)}>👁️</button>
          <button className="btn btn-ghost btn-sm btn-icon" onClick={() => navigate(`/devices/edit/${device.id}`)}>✏️</button>
          <button className="btn btn-ghost btn-sm btn-icon" onClick={handleDelete}>🗑️</button>
        </div>
      </div>
      <div className="card-subtitle">{device.commands.length} Befehl(e)</div>
    </div>
  );
}
