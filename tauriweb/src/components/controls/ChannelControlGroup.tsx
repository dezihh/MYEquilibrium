import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function ChannelControlGroup({ commands }: Props) {
  return (
    <div className="ctrl-col" style={{ maxHeight: 180 }}>
      <CommandButtonIfExists commands={commands} button={RemoteButton.ChannelUp} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.ChannelDown} />
    </div>
  );
}
