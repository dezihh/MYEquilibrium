import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useApi } from '../hooks/useApi';
import { MacroStep } from '../models/macro';

export default function CreateMacroPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get('edit');

  const { data: devices } = useApi(() => apiClient.getDevices(), []);

  const [name, setName] = useState('');
  const [steps, setSteps] = useState<MacroStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (editId) {
      apiClient.getMacros().then(macros => {
        const macro = macros.find(m => m.id === Number(editId));
        if (macro) {
          setName(macro.name);
          setSteps(macro.steps);
        }
      });
    }
  }, [editId]);

  const addStep = () => {
    const firstDevice = devices?.[0];
    if (!firstDevice) return;
    const firstCommand = firstDevice.commands[0];
    if (!firstCommand) return;
    setSteps(prev => [...prev, { deviceId: firstDevice.id, commandId: firstCommand.id, delay: 500 }]);
  };

  const removeStep = (index: number) => setSteps(prev => prev.filter((_, i) => i !== index));

  const updateStep = (index: number, field: keyof MacroStep, value: number) => {
    setSteps(prev => prev.map((s, i) => i === index ? { ...s, [field]: value } : s));
  };

  const getDeviceCommands = (deviceId: number) => devices?.find(d => d.id === deviceId)?.commands || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    setLoading(true);
    setError(null);
    try {
      if (editId) {
        await apiClient.updateMacro(Number(editId), { name, steps });
      } else {
        await apiClient.createMacro({ name, steps });
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
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <label className="form-label">Schritte</label>
            <button type="button" className="btn btn-secondary btn-sm" onClick={addStep}>+ Schritt</button>
          </div>
          {steps.length === 0 && <div className="card-subtitle">Keine Schritte. Füge Schritte hinzu.</div>}
          {steps.map((step, index) => (
            <div key={index} className="card" style={{ marginBottom: 8 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label className="form-label">Gerät</label>
                  <select className="form-control" value={step.deviceId}
                    onChange={e => {
                      const dId = Number(e.target.value);
                      const cmds = devices?.find(d => d.id === dId)?.commands || [];
                      updateStep(index, 'deviceId', dId);
                      if (cmds.length > 0) updateStep(index, 'commandId', cmds[0].id);
                    }}>
                    {devices?.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="form-label">Befehl</label>
                  <select className="form-control" value={step.commandId}
                    onChange={e => updateStep(index, 'commandId', Number(e.target.value))}>
                    {getDeviceCommands(step.deviceId).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label">Verzögerung (ms)</label>
                  <input type="number" className="form-control" value={step.delay}
                    onChange={e => updateStep(index, 'delay', Number(e.target.value))} min={0} />
                </div>
                <button type="button" className="btn btn-danger btn-sm" style={{ marginTop: 20 }}
                  onClick={() => removeStep(index)}>🗑️</button>
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
