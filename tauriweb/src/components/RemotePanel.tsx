import { Device } from '../models/device';
import { Command } from '../models/command';
import { CommandGroupType, CommandType } from '../models/enums';
import PowerControlGroup from './controls/PowerControlGroup';
import NumericControlGroup from './controls/NumericControlGroup';
import VolumeControlGroup from './controls/VolumeControlGroup';
import NavigationDPadGroup from './controls/NavigationDPadGroup';
import ChannelControlGroup from './controls/ChannelControlGroup';
import TransportControlGroup from './controls/TransportControlGroup';
import ColoredButtonsControlGroup from './controls/ColoredButtonsControlGroup';
import InputControlGroup from './controls/InputControlGroup';
import IntegrationControlGroup from './controls/IntegrationControlGroup';
import OtherControlGroup from './controls/OtherControlGroup';

interface Props {
  device: Device | null;
}

function byGroup(commands: Command[], group: CommandGroupType) {
  return commands.filter(c => c.command_group === group);
}

function has(commands: Command[], group: CommandGroupType) {
  return commands.some(c => c.command_group === group);
}

function SectionLabel({ label }: { label: string }) {
  return (
    <div className="remote-divider">
      <span>{label}</span>
    </div>
  );
}

export default function RemotePanel({ device }: Props) {
  if (!device) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🎮</div>
        <p>Kein Gerät ausgewählt</p>
      </div>
    );
  }

  const cmds = device.commands ?? [];

  if (cmds.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🎮</div>
        <p>Keine Befehle für dieses Gerät</p>
      </div>
    );
  }

  const hasPower   = has(cmds, CommandGroupType.Power);
  const hasNumeric = has(cmds, CommandGroupType.Numeric);
  const hasVol     = has(cmds, CommandGroupType.Volume);
  const hasNav     = has(cmds, CommandGroupType.Navigation);
  const hasChan    = has(cmds, CommandGroupType.Channel);
  const hasTransp  = has(cmds, CommandGroupType.Transport);
  const hasColor   = has(cmds, CommandGroupType.ColoredButtons);
  const hasInput   = has(cmds, CommandGroupType.Input);
  const hasInteg   = cmds.some(c => c.type === CommandType.Integration);
  const hasOther   = has(cmds, CommandGroupType.Other);

  return (
    <div className="remote-panel">
      <div className="remote-body">

      {/* Power */}
      {hasPower && (
        <div className="remote-section">
          <SectionLabel label="Power" />
          <PowerControlGroup commands={byGroup(cmds, CommandGroupType.Power)} />
        </div>
      )}

      {/* Numeric */}
      {hasNumeric && (
        <div className="remote-section">
          <SectionLabel label="Nummern" />
          <NumericControlGroup commands={byGroup(cmds, CommandGroupType.Numeric)} />
        </div>
      )}

      {/* Vol | D-Pad | Channel */}
      {(hasVol || hasNav || hasChan) && (
        <div className="remote-section">
          <SectionLabel label={[hasVol && 'Lautstärke', hasNav && 'Navigation', hasChan && 'Kanal'].filter(Boolean).join(' · ')} />
          <div className="ctrl-main-row" style={{ alignItems: 'center' }}>
            {hasVol && (
              <VolumeControlGroup commands={byGroup(cmds, CommandGroupType.Volume)} />
            )}
            {hasNav && (
              <NavigationDPadGroup commands={byGroup(cmds, CommandGroupType.Navigation)} />
            )}
            {hasChan && (
              <ChannelControlGroup commands={byGroup(cmds, CommandGroupType.Channel)} />
            )}
          </div>
        </div>
      )}

      {/* Transport */}
      {hasTransp && (
        <div className="remote-section">
          <SectionLabel label="Transport" />
          <TransportControlGroup commands={byGroup(cmds, CommandGroupType.Transport)} />
        </div>
      )}

      {/* Colored Buttons */}
      {hasColor && (
        <div className="remote-section">
          <SectionLabel label="Farbtasten" />
          <ColoredButtonsControlGroup commands={byGroup(cmds, CommandGroupType.ColoredButtons)} />
        </div>
      )}

      {/* Input */}
      {hasInput && (
        <div className="remote-section">
          <SectionLabel label="Eingang" />
          <InputControlGroup commands={cmds} />
        </div>
      )}

      {/* Integration */}
      {hasInteg && (
        <div className="remote-section">
          <SectionLabel label="Integration" />
          <IntegrationControlGroup commands={cmds} />
        </div>
      )}

      {/* Other */}
      {hasOther && (
        <div className="remote-section">
          <SectionLabel label="Sonstiges" />
          <OtherControlGroup commands={cmds} />
        </div>
      )}

      </div>
    </div>
  );
}
