import { useAppContext } from '../context/AppContext';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import SceneCard from '../components/SceneCard';
import { useNavigate } from 'react-router-dom';

export default function ScenesPage() {
  const { currentScene, setCurrentScene } = useAppContext();
  const { data: scenes, loading, error, reload } = useApi(() => apiClient.getScenes(), []);
  const navigate = useNavigate();

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Szenen</h2>
      </div>
      {scenes && scenes.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎬</div>
          <p>Keine Szenen vorhanden</p>
          <p>Erstelle eine neue Szene mit dem + Button</p>
        </div>
      )}
      {scenes?.map((scene) => (
        <SceneCard
          key={scene.id}
          scene={scene}
          isActive={currentScene === scene.id}
          onRefresh={reload}
          onSceneStart={setCurrentScene}
          onSceneStop={() => setCurrentScene(null)}
        />
      ))}
      <button className="fab" onClick={() => navigate('/scenes/create')}>+</button>
    </div>
  );
}
