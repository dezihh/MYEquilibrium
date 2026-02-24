import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useAppContext } from '../context/AppContext';
import { useState } from 'react';

export default function SceneDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentScene, setCurrentScene } = useAppContext();
  const { data: scene, loading, error } = useApi(() => apiClient.getScenes().then(s => s.find(x => x.id === Number(id))!), [id]);
  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const { data: macros } = useApi(() => apiClient.getMacros(), []);
  const [actionLoading, setActionLoading] = useState(false);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error || !scene) return <div className="error-container">Szene nicht gefunden</div>;

  const isActive = currentScene === scene.id;

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await apiClient.startScene(scene.id);
      setCurrentScene(scene.id);
    } catch (e) { alert(`Fehler: ${e}`); }
    finally { setActionLoading(false); }
  };

  const handleStop = async () => {
    setActionLoading(true);
    try {
      await apiClient.stopScenes();
      setCurrentScene(null);
    } catch (e) { alert(`Fehler: ${e}`); }
    finally { setActionLoading(false); }
  };

  const handleDelete = async () => {
    if (!confirm(`Szene "${scene.name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteScene(scene.id);
      navigate('/scenes');
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  const getDeviceName = (devId: number) => devices?.find(d => d.id === devId)?.name || `Gerät ${devId}`;
  const getMacroName = (macroId: number | null) => macroId ? macros?.find(m => m.id === macroId)?.name || `Makro ${macroId}` : 'Keins';

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title" style={{ fontSize: '1.3rem' }}>{scene.name}</div>
            {isActive && <span className="badge badge-success">Aktiv</span>}
          </div>
        </div>

        <div style={{ marginBottom: 8 }}>
          <div className="form-label">Geräte</div>
          {scene.devices.length === 0 ? (
            <span className="badge">Keine</span>
          ) : scene.devices.map(dId => (
            <span key={dId} className="badge badge-primary" style={{ marginRight: 4 }}>{getDeviceName(dId)}</span>
          ))}
        </div>

        <div style={{ marginBottom: 8 }}>
          <div className="form-label">Start-Makro</div>
          <span className="badge badge-primary">{getMacroName(scene.startMacro)}</span>
        </div>

        <div style={{ marginBottom: 16 }}>
          <div className="form-label">Stop-Makro</div>
          <span className="badge badge-primary">{getMacroName(scene.stopMacro)}</span>
        </div>

        <div className="btn-group">
          {!isActive ? (
            <button className="btn btn-primary" onClick={handleStart} disabled={actionLoading}>▶ Starten</button>
          ) : (
            <button className="btn btn-danger" onClick={handleStop} disabled={actionLoading}>⏹ Stoppen</button>
          )}
          <button className="btn btn-secondary" onClick={() => navigate(`/scenes/edit/${scene.id}`)}>✏️ Bearbeiten</button>
          <button className="btn btn-danger" onClick={handleDelete}>🗑️ Löschen</button>
        </div>
      </div>
    </div>
  );
}
