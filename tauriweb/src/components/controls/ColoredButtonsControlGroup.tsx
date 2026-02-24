import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function ColoredButtonsControlGroup({ commands }: Props) {
  return (
    <div className="ctrl-grid-4" style={{ maxWidth: 220 }}>
      <CommandButtonIfExists commands={commands} button={RemoteButton.Red} color="#ef5350" />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Green} color="#66bb6a" />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Yellow} color="#ffa726" />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Blue} color="#42a5f5" />
    </div>
  );
}
