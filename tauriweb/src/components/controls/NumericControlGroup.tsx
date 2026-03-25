import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function NumericControlGroup({ commands }: Props) {
  return (
    <div className="remote-numeric-grid">
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number1} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number2} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number3} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number4} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number5} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number6} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number7} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number8} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number9} />
      {/* bottom row: empty – 0 – empty */}
      <div style={{ width: 44, height: 44 }} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Number0} />
      <div style={{ width: 44, height: 44 }} />
    </div>
  );
}
