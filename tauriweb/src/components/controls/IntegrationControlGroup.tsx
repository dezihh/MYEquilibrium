import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { CommandType } from '../../models/enums';

interface Props {
  commands: Command[];
}

export default function IntegrationControlGroup({ commands }: Props) {
  const integrationCommands = commands.filter(
    (command) => command.type === CommandType.Integration
  );

  if (integrationCommands.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 460, marginBottom: 8 }}>
      {integrationCommands.map((command) => (
        <button
          key={command.id}
          className="ctrl-btn"
          style={{ fontSize: '0.75rem', padding: '4px 10px', minWidth: 'unset', height: 'unset' }}
          onClick={() => apiClient.sendCommand(command.id).catch((e) => alert(`Fehler: ${e}`))}
          title={command.name}
        >
          {command.name}
        </button>
      ))}
    </div>
  );
}