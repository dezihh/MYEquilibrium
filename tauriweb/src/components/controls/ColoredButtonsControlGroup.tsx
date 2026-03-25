import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';

interface Props { commands: Command[]; }

const COLOR_MAP: Partial<Record<RemoteButton, string>> = {
  [RemoteButton.Red]:    '#c0392b',
  [RemoteButton.Green]:  '#27ae60',
  [RemoteButton.Yellow]: '#f39c12',
  [RemoteButton.Blue]:   '#2980b9',
};

const BUTTONS = [RemoteButton.Red, RemoteButton.Green, RemoteButton.Yellow, RemoteButton.Blue];

export default function ColoredButtonsControlGroup({ commands }: Props) {
  const present = BUTTONS.filter(b => commands.some(c => c.button === b));
  if (present.length === 0) return null;

  return (
    <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
      {present.map(button => {
        const cmd = commands.find(c => c.button === button)!;
        return (
          <button
            key={button}
            className="ctrl-btn colored-btn"
            style={{ background: COLOR_MAP[button], borderColor: COLOR_MAP[button] }}
            title={cmd.name}
            onClick={() => apiClient.sendCommand(cmd.id).catch(e => alert(`Fehler: ${e}`))}
          />
        );
      })}
    </div>
  );
}
