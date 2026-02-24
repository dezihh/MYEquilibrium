import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { useApi } from '../hooks/useApi';
import {
  RemoteButton, CommandType, CommandGroupType, CommandTypeLabel,
  CommandGroupTypeLabel, RemoteButtonsByGroup,
  BluetoothCommandType, BluetoothCommandTypeLabel, BluetoothCommandsByType,
  NetworkRequestType, NetworkRequestTypeCanHaveBody,
  IntegrationAction, IntegrationActionLabel,
} from '../models/enums';

export default function CreateCommandPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { data: devices } = useApi(() => apiClient.getDevices(), []);
  const { data: haLights } = useApi(() => apiClient.getHaLights(), []);

  const [name, setName] = useState('');
  const [deviceId, setDeviceId] = useState<number | null>(null);
  const [group, setGroup] = useState<CommandGroupType>(CommandGroupType.Power);
  const [type, setType] = useState<CommandType>(CommandType.Infrared);
  const [button, setButton] = useState<RemoteButton>(RemoteButton.PowerToggle);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // IR
  const [recording, setRecording] = useState(false);
  const [recordStatus, setRecordStatus] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Bluetooth
  const [btType, setBtType] = useState<BluetoothCommandType>(BluetoothCommandType.RegularKey);
  const [btCommand, setBtCommand] = useState(BluetoothCommandsByType[BluetoothCommandType.RegularKey][0]);
  const [btKey, setBtKey] = useState('');

  // Network
  const [host, setHost] = useState('');
  const [method, setMethod] = useState<NetworkRequestType>(NetworkRequestType.Get);
  const [body, setBody] = useState('');

  // Integration
  const [integrationAction, setIntegrationAction] = useState<IntegrationAction>(IntegrationAction.ToggleLight);
  const [integrationEntity, setIntegrationEntity] = useState('');
  const [integrationService, setIntegrationService] = useState('');
  const [integrationData, setIntegrationData] = useState('');

  const buttonsForGroup = RemoteButtonsByGroup[group] ?? [];

  const handleGroupChange = (g: CommandGroupType) => {
    setGroup(g);
    const btns = RemoteButtonsByGroup[g] ?? [];
    if (btns.length > 0) setButton(btns[0]);
  };

  const handleTypeChange = (newType: CommandType) => {
    setType(newType);
    if (newType === CommandType.Integration) {
      const integrationButtons = RemoteButtonsByGroup[CommandGroupType.Other] ?? [];
      setGroup(CommandGroupType.Other);
      if (integrationButtons.length > 0) setButton(integrationButtons[0]);
    }
  };

  useEffect(() => {
    const typeParam = searchParams.get('type');
    if (typeParam === CommandType.Integration) {
      handleTypeChange(CommandType.Integration);
    }

    const deviceParam = searchParams.get('deviceId');
    if (deviceParam) {
      const parsed = Number(deviceParam);
      if (!Number.isNaN(parsed)) setDeviceId(parsed);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const startRecording = useCallback(() => {
    setRecording(true);
    setRecordStatus('Warte auf IR-Signal...');
    const ws = apiClient.createCommandsWebSocket(
      (data: unknown) => {
        const msg = data as { status?: string };
        setRecordStatus(msg.status ?? 'Signal empfangen');
        setRecording(false);
        ws.close();
      },
      () => { setRecordStatus('❌ WebSocket Fehler'); setRecording(false); }
    );
    wsRef.current = ws;
  }, []);

  const stopRecording = () => {
    wsRef.current?.close();
    setRecording(false);
    setRecordStatus(null);
  };

  const buildCommandPayload = () => {
    const base = {
      name, button, type, command_group: group,
      device_id: deviceId,
      host: null as string | null,
      method: null as string | null,
      body: null as string | null,
      bt_action: null as string | null,
      bt_media_action: null as string | null,
      integration_action: null as string | null,
      integration_entity: null as string | null,
    };
    if (type === CommandType.Network) {
      base.host = host;
      base.method = method;
      if (NetworkRequestTypeCanHaveBody[method]) base.body = body || null;
    } else if (type === CommandType.Bluetooth) {
      if (btType === BluetoothCommandType.RegularKey) {
        base.bt_action = btCommand === 'other' ? btKey : btCommand;
      } else {
        base.bt_media_action = btCommand;
      }
    } else if (type === CommandType.Integration) {
      base.integration_action = integrationAction;
      if (integrationAction === IntegrationAction.CallService) {
        base.integration_entity = integrationService.trim();
        base.body = integrationData.trim() || null;
      } else {
        base.integration_entity = integrationEntity.trim();
      }
    }
    return base;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name ist erforderlich'); return; }
    if (!deviceId) { setError('Gerät ist erforderlich'); return; }
    if (type === CommandType.Integration) {
      if (integrationAction === IntegrationAction.CallService) {
        if (!integrationService.trim()) {
          setError('Service ist erforderlich (Format: domain.service)');
          return;
        }
        if (!integrationService.includes('.')) {
          setError('Service muss im Format domain.service angegeben werden');
          return;
        }
        if (integrationData.trim()) {
          try {
            JSON.parse(integrationData);
          } catch {
            setError('JSON-Daten sind ungültig');
            return;
          }
        }
      } else if (!integrationEntity.trim()) {
        setError('Entity ist für Integrationsbefehle erforderlich');
        return;
      }
    }
    if (type === CommandType.Bluetooth && btType === BluetoothCommandType.RegularKey && btCommand === 'other' && !btKey.trim()) {
      setError('Tastencode ist erforderlich, wenn "other" gewählt ist');
      return;
    }
    setLoading(true); setError(null);
    try {
      await apiClient.createCommand(buildCommandPayload());
      navigate(-1);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally { setLoading(false); }
  };

  return (
    <div>
      {error && <div className="error-container">{error}</div>}
      <form onSubmit={handleSubmit}>

        {/* Gerät */}
        <div className="form-group">
          <label className="form-label">Gerät</label>
          <select className="form-control" value={deviceId ?? ''} onChange={e => setDeviceId(Number(e.target.value))}>
            <option value="">Gerät auswählen</option>
            {devices?.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>

        {/* Name */}
        <div className="form-group">
          <label className="form-label">Name</label>
          <input className="form-control" value={name} onChange={e => setName(e.target.value)} placeholder="Befehlsname" />
        </div>

        {/* Gruppe */}
        <div className="form-group">
          <label className="form-label">Befehlsgruppe</label>
          <select className="form-control" value={group} onChange={e => handleGroupChange(e.target.value as CommandGroupType)}>
            {Object.values(CommandGroupType).map(g => <option key={g} value={g}>{CommandGroupTypeLabel[g]}</option>)}
          </select>
        </div>

        {/* Typ */}
        <div className="form-group">
          <label className="form-label">Typ</label>
          <select className="form-control" value={type} onChange={e => handleTypeChange(e.target.value as CommandType)}>
            {Object.values(CommandType).filter(t => t !== CommandType.Script).map(t => (
              <option key={t} value={t}>{CommandTypeLabel[t]}</option>
            ))}
          </select>
        </div>

        {/* Taste */}
        <div className="form-group">
          <label className="form-label">Taste</label>
          <select className="form-control" value={button} onChange={e => setButton(e.target.value as RemoteButton)}>
            {buttonsForGroup.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        {/* ===== IR Section ===== */}
        {type === CommandType.Infrared && (
          <div className="form-group">
            <label className="form-label">IR-Signal aufnehmen</label>
            {recordStatus && <div style={{ marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{recordStatus}</div>}
            <div className="btn-group">
              {!recording
                ? <button type="button" className="btn btn-secondary" onClick={startRecording}>🔴 Aufnehmen</button>
                : <button type="button" className="btn btn-danger" onClick={stopRecording}>⏹ Stopp</button>}
            </div>
          </div>
        )}

        {/* ===== Bluetooth Section ===== */}
        {type === CommandType.Bluetooth && (
          <>
            <div className="form-group">
              <label className="form-label">Tastentyp</label>
              <select className="form-control" value={btType} onChange={e => {
                const t = e.target.value as BluetoothCommandType;
                setBtType(t);
                setBtCommand(BluetoothCommandsByType[t][0]);
              }}>
                {Object.values(BluetoothCommandType).map(t => <option key={t} value={t}>{BluetoothCommandTypeLabel[t]}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Taste</label>
              <select className="form-control" value={btCommand} onChange={e => setBtCommand(e.target.value as any)}>
                {BluetoothCommandsByType[btType].map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            {btCommand === 'other' && (
              <div className="form-group">
                <label className="form-label">Tastencode</label>
                <input className="form-control" value={btKey} onChange={e => setBtKey(e.target.value)} placeholder="z.B. KEY_A" />
              </div>
            )}
          </>
        )}

        {/* ===== Network Section ===== */}
        {type === CommandType.Network && (
          <>
            <div className="form-group">
              <label className="form-label">Host (URL)</label>
              <input className="form-control" value={host} onChange={e => setHost(e.target.value)} placeholder="http://192.168.1.1/api/action" />
            </div>
            <div className="form-group">
              <label className="form-label">HTTP-Methode</label>
              <select className="form-control" value={method} onChange={e => setMethod(e.target.value as NetworkRequestType)}>
                {Object.values(NetworkRequestType).map(m => <option key={m} value={m}>{m.toUpperCase()}</option>)}
              </select>
            </div>
            {NetworkRequestTypeCanHaveBody[method] && (
              <div className="form-group">
                <label className="form-label">Body</label>
                <input className="form-control" value={body} onChange={e => setBody(e.target.value)} placeholder='{"key": "value"}' />
              </div>
            )}
          </>
        )}

        {/* ===== Integration Section ===== */}
        {type === CommandType.Integration && (
          <>
            <div className="form-group">
              <label className="form-label">Aktion</label>
              <select className="form-control" value={integrationAction} onChange={e => setIntegrationAction(e.target.value as IntegrationAction)}>
                {Object.values(IntegrationAction).map(a => <option key={a} value={a}>{IntegrationActionLabel[a]}</option>)}
              </select>
            </div>
            <div className="form-group">
              {integrationAction === IntegrationAction.CallService ? (
                <>
                  <label className="form-label">Service (domain.service)</label>
                  <input className="form-control" value={integrationService} onChange={e => setIntegrationService(e.target.value)} placeholder="scene.turn_on" />
                  <label className="form-label" style={{ marginTop: 8 }}>Daten (JSON, optional)</label>
                  <input className="form-control" value={integrationData} onChange={e => setIntegrationData(e.target.value)} placeholder='{"entity_id":"scene.evening"}' />
                </>
              ) : (
                <>
                  <label className="form-label">Entity</label>
                  {haLights && haLights.length > 0 ? (
                    <select className="form-control" value={integrationEntity} onChange={e => setIntegrationEntity(e.target.value)}>
                      <option value="">Entity auswählen</option>
                      {haLights.map(entity => <option key={entity} value={entity}>{entity}</option>)}
                    </select>
                  ) : (
                    <input className="form-control" value={integrationEntity} onChange={e => setIntegrationEntity(e.target.value)} placeholder="light.ceiling_lamp" />
                  )}
                </>
              )}
            </div>
          </>
        )}

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Abbrechen</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Speichern...' : 'Speichern'}</button>
        </div>
      </form>
    </div>
  );
}


