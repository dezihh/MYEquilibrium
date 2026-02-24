import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function MacroListPage() {
  const { data: macros, loading, error, reload } = useApi(() => apiClient.getMacros(), []);
  const navigate = useNavigate();
  const [executing, setExecuting] = useState<number | null>(null);

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Makro "${name}" wirklich löschen?`)) return;
    try {
      await apiClient.deleteMacro(id);
      reload();
    } catch (e) { alert(`Fehler: ${e}`); }
  };

  const handleExecute = async (id: number) => {
    setExecuting(id);
    try {
      await apiClient.executeMacro(id);
    } catch (e) { alert(`Fehler: ${e}`); }
    finally { setExecuting(null); }
  };

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Makros</h2>
        <button className="btn btn-primary btn-sm" onClick={() => navigate('/settings/macros/create')}>+ Neu</button>
      </div>
      {macros?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">⚡</div>
          <p>Keine Makros vorhanden</p>
        </div>
      )}
      {macros?.map(macro => (
        <div key={macro.id} className="list-item">
          <div>
            <div style={{ fontWeight: 600 }}>{macro.name}</div>
            <div className="card-subtitle">{macro.steps.length} Schritt(e)</div>
          </div>
          <div className="btn-group">
            <button className="btn btn-primary btn-sm" onClick={() => handleExecute(macro.id)} disabled={executing === macro.id}>
              {executing === macro.id ? '...' : '▶'}
            </button>
            <button className="btn btn-ghost btn-sm btn-icon" onClick={() => navigate(`/settings/macros/create?edit=${macro.id}`)}>✏️</button>
            <button className="btn btn-ghost btn-sm btn-icon" onClick={() => handleDelete(macro.id, macro.name)}>🗑️</button>
          </div>
        </div>
      ))}
    </div>
  );
}
