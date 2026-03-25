import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import RemoteIcon from './RemoteIcon';

interface Props {
  commands: Command[];
  button: RemoteButton;
  useName?: boolean;
  color?: string;
  primary?: boolean;
}

export default function CommandButtonIfExists({ commands, button, useName = false, color, primary = false }: Props) {
  const command = commands.find(c => c.button === button);

  if (!command) return <div style={{ width: primary ? 52 : 44, height: primary ? 52 : 44 }} />;

  const handleClick = () => {
    apiClient.sendCommand(command.id).catch(e => alert(`Fehler: ${e}`));
  };

  const label = useName
    ? command.name
    : <RemoteIcon button={button} />;

  return (
    <button
      onClick={handleClick}
      className={primary ? 'ctrl-btn ctrl-btn--primary' : 'ctrl-btn'}
      style={color ? { color } : undefined}
      title={command.name}
    >
      {label}
    </button>
  );
}
