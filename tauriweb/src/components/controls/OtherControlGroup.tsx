import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { CommandGroupType } from '../../models/enums';

interface Props { commands: Command[]; }

export default function OtherControlGroup({ commands }: Props) {
  const otherCmds = commands.filter(c => c.command_group === CommandGroupType.Other);
  if (otherCmds.length === 0) return null;

  return (
    <div className="remote-other-row">
      {otherCmds.map(cmd => (
        <button
          key={cmd.id}
          className="ctrl-btn"
          title={cmd.name}
          onClick={() => apiClient.sendCommand(cmd.id).catch(e => alert(`Fehler: ${e}`))}
        >
          {cmd.name}
        </button>
      ))}
    </div>
  );
}
