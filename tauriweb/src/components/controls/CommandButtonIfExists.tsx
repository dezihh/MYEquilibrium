import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';

const BUTTON_ICONS: Partial<Record<RemoteButton, string>> = {
  [RemoteButton.PowerToggle]: '⏻',
  [RemoteButton.PowerOn]: '🟢',
  [RemoteButton.PowerOff]: '🔴',
  [RemoteButton.VolumeUp]: '🔊',
  [RemoteButton.VolumeDown]: '🔉',
  [RemoteButton.Mute]: '🔇',
  [RemoteButton.ChannelUp]: '▲',
  [RemoteButton.ChannelDown]: '▼',
  [RemoteButton.DirectionUp]: '↑',
  [RemoteButton.DirectionDown]: '↓',
  [RemoteButton.DirectionLeft]: '←',
  [RemoteButton.DirectionRight]: '→',
  [RemoteButton.Select]: '⏎',
  [RemoteButton.Back]: '↩',
  [RemoteButton.Home]: '⌂',
  [RemoteButton.Menu]: 'Menü',
  [RemoteButton.Exit]: 'Exit',
  [RemoteButton.Guide]: 'Guide',
  [RemoteButton.Info]: 'ℹ',
  [RemoteButton.Play]: '▶',
  [RemoteButton.Pause]: '⏸',
  [RemoteButton.PlayPause]: '⏯',
  [RemoteButton.Stop]: '⏹',
  [RemoteButton.FastForward]: '⏩',
  [RemoteButton.Rewind]: '⏪',
  [RemoteButton.NextTrack]: '⏭',
  [RemoteButton.PreviousTrack]: '⏮',
  [RemoteButton.Record]: '⏺',
  [RemoteButton.Red]: '🟥',
  [RemoteButton.Green]: '🟩',
  [RemoteButton.Yellow]: '🟨',
  [RemoteButton.Blue]: '🟦',
  [RemoteButton.BrightnessUp]: '🔆',
  [RemoteButton.BrightnessDown]: '🔅',
  [RemoteButton.TurnOn]: '🟢',
  [RemoteButton.TurnOff]: '🔴',
};

interface Props {
  commands: Command[];
  button: RemoteButton;
  useName?: boolean;
  color?: string;
}

export default function CommandButtonIfExists({ commands, button, useName = false, color }: Props) {
  const command = commands.find(c => c.button === button);

  if (!command) return <div style={{ width: 44, height: 44 }} />;

  const handleClick = () => {
    apiClient.sendCommand(command.id).catch(e => alert(`Fehler: ${e}`));
  };

  const label = useName ? command.name : (BUTTON_ICONS[button] ?? button);

  return (
    <button
      onClick={handleClick}
      className="ctrl-btn"
      style={color ? { color } : undefined}
      title={command.name}
    >
      {label}
    </button>
  );
}
