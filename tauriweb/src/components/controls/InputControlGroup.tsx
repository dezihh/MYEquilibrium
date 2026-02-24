import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { CommandGroupType } from '../../models/enums';

interface Props { commands: Command[]; }

export default function InputControlGroup({ commands }: Props) {
  const inputCommands = commands.filter(c => c.command_group === CommandGroupType.Input);
  if (inputCommands.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 320, marginBottom: 8 }}>
      {inputCommands.map(cmd => (
        <button
          key={cmd.id}
          className="ctrl-btn"
          style={{ fontSize: '0.75rem', padding: '4px 10px', minWidth: 'unset', height: 'unset' }}
          onClick={() => apiClient.sendCommand(cmd.id).catch(e => alert(`Fehler: ${e}`))}
          title={cmd.name}
        >
          {cmd.name}
        </button>
      ))}
    </div>
  );
}
