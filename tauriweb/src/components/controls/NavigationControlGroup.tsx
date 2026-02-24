import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function NavigationControlGroup({ commands }: Props) {
  return (
    <div className="ctrl-grid-3" style={{ maxWidth: 165 }}>
      <CommandButtonIfExists commands={commands} button={RemoteButton.Exit} useName />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionUp} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Guide} useName />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionLeft} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Select} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionRight} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Menu} useName />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionDown} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Back} useName />
    </div>
  );
}
