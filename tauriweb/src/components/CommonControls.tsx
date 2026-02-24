import { Device } from '../models/device';
import { Command } from '../models/command';
import { CommandGroupType } from '../models/enums';
import NavigationControlGroup from './controls/NavigationControlGroup';
import VolumeControlGroup from './controls/VolumeControlGroup';
import ChannelControlGroup from './controls/ChannelControlGroup';
import TransportControlGroup from './controls/TransportControlGroup';
import ColoredButtonsControlGroup from './controls/ColoredButtonsControlGroup';
import InputControlGroup from './controls/InputControlGroup';
import IntegrationControlGroup from './controls/IntegrationControlGroup';

interface Props {
  devices: Device[];
}

function filterByGroup(commands: Command[], group: CommandGroupType) {
  return commands.filter(c => c.command_group === group);
}

export default function CommonControls({ devices }: Props) {
  const allCommands = devices.flatMap(d => d.commands ?? []);

  const navCmds = filterByGroup(allCommands, CommandGroupType.Navigation);
  const volCmds = filterByGroup(allCommands, CommandGroupType.Volume);
  const chanCmds = filterByGroup(allCommands, CommandGroupType.Channel);
  const transportCmds = filterByGroup(allCommands, CommandGroupType.Transport);
  const colorCmds = filterByGroup(allCommands, CommandGroupType.ColoredButtons);

  const hasAny = allCommands.length > 0;

  if (!hasAny) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🎮</div>
        <p>Keine Befehle verfügbar</p>
      </div>
    );
  }

  return (
    <div className="common-controls">
      <IntegrationControlGroup commands={allCommands} />
      <InputControlGroup commands={allCommands} />
      <div className="ctrl-main-row">
        <VolumeControlGroup commands={volCmds} />
        <NavigationControlGroup commands={navCmds} />
        <ChannelControlGroup commands={chanCmds} />
      </div>
      <TransportControlGroup commands={transportCmds} />
      <ColoredButtonsControlGroup commands={colorCmds} />
    </div>
  );
}
