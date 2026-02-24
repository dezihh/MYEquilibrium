import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useApi } from '../hooks/useApi';
import { Command } from '../models/command';

interface MacroEntry { commandId: number; delay: number; }

export default function CreateMacroPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get('edit');

  const { data: devices } = useApi(() => apiClient.getDevices(), []);

  const [name, setName] = useState('');
  const [entries, setEntries] = useState<MacroEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allCommands: Command[] = devices?.flatMap(d => d.commands) ?? [];

  useEffect(() => {
    if (editId) {
      apiClient.getMacros().then(macros => {
        const macro = macros.find(m => m.id === Number(editId));
        if (macro) {
          setName(macro.name);
          const newEntries: MacroEntry[] = macro.command_ids.map((cid, i) => ({
            commandId: cid,
            delay: macro.delays[i] ?? 500,
          }));
          setEntries(newEntries);
        }
      });
    }
  }, [editId]);

  const addEntry = () => {
    if (allCommands.length === 0) return;
    setEntries(prev => [...prev, { commandId: allCommands[0].id, delay: 500 }]);
  };

  const removeEntry = (index: number) => setEntries(prev => prev.filter((_, i) => i !== index));

  const updateEntry = (index: number, field: keyof MacroEntry, value: number) => {
    setEntries(prev => prev.map((e, i) => i === index ? { ...e, [field]: value } : e));
  };

  const getCommandLabel = (cmd: Command) => {
    const device = devices?.find(d => d.commands.some(c => c.id === cmd.id));
    return device ? `${device.name} → ${cmd.name}` : cmd.name;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      const command_ids = entries.map(e => e.commandId);
      const delays = entries.map(e => e.delay);
      if (editId) {
        await apiClient.updateMacro(Number(editId), { name, command_ids, delays });
      } else {
        await apiClient.createMacro({ name, command_ids, delays });
      }
      navigate('/settings/macros');
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
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Makroname" />
        </div>

        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <label className="form-label" style={{ marginBottom: 0 }}>Schritte</label>
            <button type="button" className="btn btn-secondary btn-sm" onClick={addEntry} disabled={allCommands.length === 0}>
              + Schritt
            </button>
          </div>
          {entries.length === 0 && <div className="card-subtitle">Keine Schritte vorhanden.</div>}
          {entries.map((entry, index) => (
            <div key={index} className="card" style={{ marginBottom: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span className="card-subtitle" style={{ minWidth: 24 }}>{index + 1}.</span>
                <select className="form-control" value={entry.commandId}
                  onChange={e => updateEntry(index, 'commandId', Number(e.target.value))} style={{ flex: 1 }}>
                  {allCommands.map(c => (
                    <option key={c.id} value={c.id}>{getCommandLabel(c)}</option>
                  ))}
                </select>
                <button type="button" className="btn btn-danger btn-sm btn-icon" onClick={() => removeEntry(index)}>🗑️</button>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <label className="form-label" style={{ marginBottom: 0, minWidth: 130 }}>Verzögerung (ms)</label>
                <input type="number" className="form-control" value={entry.delay}
                  onChange={e => updateEntry(index, 'delay', Number(e.target.value))} min={0} style={{ width: 100 }} />
              </div>
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Abbrechen</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Speichern...' : 'Speichern'}</button>
        </div>
      </form>
    </div>
  );
}


