import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

export default function TransportControlGroup({ commands }: Props) {
  return (
    <div style={{ maxWidth: 320 }}>
      <div className="ctrl-grid-5">
        <CommandButtonIfExists commands={commands} button={RemoteButton.Play} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.Pause} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.PlayPause} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.Stop} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.Record} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.PreviousTrack} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.Rewind} />
        <div />
        <CommandButtonIfExists commands={commands} button={RemoteButton.FastForward} />
        <CommandButtonIfExists commands={commands} button={RemoteButton.NextTrack} />
      </div>
    </div>
  );
}
