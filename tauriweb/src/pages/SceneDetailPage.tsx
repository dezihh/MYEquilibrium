import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useAppContext } from '../context/AppContext';
import { useState } from 'react';
import CommonControls from '../components/CommonControls';

export default function SceneDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentScene, setCurrentScene } = useAppContext();
  const { data: scene, loading, error } = useApi(
    () => apiClient.getScenes().then(s => s.find(x => x.id === Number(id))!), [id]
  );
  const { data: allDevices } = useApi(() => apiClient.getDevices(), []);
  const { data: macros } = useApi(() => apiClient.getMacros(), []);
  const [actionLoading, setActionLoading] = useState(false);

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error || !scene) return <div className="error-container">Szene nicht gefunden</div>;

  const isActive = currentScene === scene.id;
  const sceneDevices = allDevices?.filter(d => scene.device_ids.includes(d.id)) ?? [];

  const handleStart = async () => {
    setActionLoading(true);
    try { await apiClient.startScene(scene.id); setCurrentScene(scene.id); }
    catch (e) { alert(`Fehler: ${e}`); }
    finally { setActionLoading(false); }
  };

  const handleStop = async () => {
    setActionLoading(true);
    try { await apiClient.stopScenes(); setCurrentScene(null); }
    catch (e) { alert(`Fehler: ${e}`); }
    finally { setActionLoading(false); }
  };

  const handleDelete = async () => {
    if (!confirm(`Szene "${scene.name}" wirklich löschen?`)) return;
    try { await apiClient.deleteScene(scene.id); navigate('/scenes'); }
    catch (e) { alert(`Fehler: ${e}`); }
  };

  const getMacroName = (macroId: number | null, macroObj?: { name: string } | null) => {
    if (macroObj) return macroObj.name;
    if (macroId) return macros?.find(m => m.id === macroId)?.name ?? `Makro ${macroId}`;
    return 'Keins';
  };

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
          {sceneDevices.length === 0
            ? <span className="badge">Keine</span>
            : sceneDevices.map(d => (
              <span key={d.id} className="badge badge-primary" style={{ marginRight: 4 }}>{d.name}</span>
            ))
          }
        </div>

        <div style={{ marginBottom: 8 }}>
          <div className="form-label">Start-Makro</div>
          <span className="badge badge-primary">{getMacroName(scene.start_macro_id, scene.start_macro)}</span>
        </div>

        <div style={{ marginBottom: 16 }}>
          <div className="form-label">Stop-Makro</div>
          <span className="badge badge-primary">{getMacroName(scene.stop_macro_id, scene.stop_macro)}</span>
        </div>

        <div className="btn-group">
          {!isActive
            ? <button className="btn btn-primary" onClick={handleStart} disabled={actionLoading}>▶ Starten</button>
            : <button className="btn btn-danger" onClick={handleStop} disabled={actionLoading}>⏹ Stoppen</button>
          }
          <button className="btn btn-secondary" onClick={() => navigate(`/scenes/edit/${scene.id}`)}>✏️ Bearbeiten</button>
          <button className="btn btn-danger" onClick={handleDelete}>🗑️ Löschen</button>
        </div>
      </div>

      {sceneDevices.length > 0 && (
        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>Fernbedienung</div>
          <CommonControls devices={sceneDevices} />
        </div>
      )}
    </div>
  );
}


