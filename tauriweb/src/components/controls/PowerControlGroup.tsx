import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function PowerControlGroup({ commands }: Props) {
  return (
    <div className="remote-power-row">
      <CommandButtonIfExists commands={commands} button={RemoteButton.PowerOff} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.PowerToggle} primary />
      <CommandButtonIfExists commands={commands} button={RemoteButton.PowerOn} />
    </div>
  );
}
