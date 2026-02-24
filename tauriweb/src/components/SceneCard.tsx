import { Scene } from '../models/scene';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useState } from 'react';

interface Props {
  scene: Scene;
  isActive: boolean;
  onRefresh: () => void;
  onSceneStart: (id: number) => void;
  onSceneStop: () => void;
}

export default function SceneCard({ scene, isActive, onRefresh, onSceneStart, onSceneStop }: Props) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    try {
      await apiClient.startScene(scene.id);
      onSceneStart(scene.id);
    } catch (e) {
      alert(`Fehler: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await apiClient.stopScenes();
      onSceneStop();
    } catch (e) {
      alert(`Fehler: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Szene "${scene.name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteScene(scene.id);
      onRefresh();
    } catch (e) {
      alert(`Fehler: ${e}`);
    }
  };

  return (
    <div className={`card ${isActive ? 'active' : ''}`}>
      <div className="card-header">
        <div>
          <div className="card-title">{scene.name}</div>
          {isActive && <span className="badge badge-success">Aktiv</span>}
        </div>
        <div className="btn-group">
          <button className="btn btn-ghost btn-sm btn-icon" onClick={() => navigate(`/scenes/edit/${scene.id}`)}>✏️</button>
          <button className="btn btn-ghost btn-sm btn-icon" onClick={handleDelete}>🗑️</button>
        </div>
      </div>
      <div className="card-subtitle">{scene.devices.length} Gerät(e)</div>
      <div className="btn-group" style={{ marginTop: 12 }}>
        {!isActive ? (
          <button className="btn btn-primary btn-sm" onClick={handleStart} disabled={loading}>▶ Starten</button>
        ) : (
          <button className="btn btn-danger btn-sm" onClick={handleStop} disabled={loading}>⏹ Stoppen</button>
        )}
        <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/scenes/${scene.id}`)}>Details</button>
      </div>
    </div>
  );
}
