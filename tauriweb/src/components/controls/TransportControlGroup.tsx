import apiClient from '../../api/apiClient';
import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import RemoteIcon from './RemoteIcon';

interface Props { commands: Command[]; }

function TBtn({ commands, button, accent = false }: { commands: Command[]; button: RemoteButton; accent?: boolean }) {
  const cmd = commands.find(c => c.button === button);
  if (!cmd) return <div style={{ width: 44, height: 44 }} />;
  return (
    <button
      className={accent ? 'ctrl-btn ctrl-btn--accent' : 'ctrl-btn'}
      title={cmd.name}
      onClick={() => apiClient.sendCommand(cmd.id).catch(e => alert(`Fehler: ${e}`))}
    >
      <RemoteIcon button={button} />
    </button>
  );
}

export default function TransportControlGroup({ commands }: Props) {
  const has = (b: RemoteButton) => commands.some(c => c.button === b);

  // Middle of main row: prefer PlayPause, fallback Play
  const mainMiddle = has(RemoteButton.PlayPause) ? RemoteButton.PlayPause : RemoteButton.Play;

  // Secondary row: Pause (only if Play also exists), Stop, Record
  const showPause  = has(RemoteButton.Pause) && has(RemoteButton.Play);
  const showStop   = has(RemoteButton.Stop);
  const showRecord = has(RemoteButton.Record);
  const hasSecondary = showPause || showStop || showRecord;

  return (
    <div className="transport-group">
      {/* Main row: |< << ▶/⏯ >> >| */}
      <div className="transport-main-row">
        <TBtn commands={commands} button={RemoteButton.PreviousTrack} />
        <TBtn commands={commands} button={RemoteButton.Rewind} />
        <TBtn commands={commands} button={mainMiddle} accent />
        <TBtn commands={commands} button={RemoteButton.FastForward} />
        <TBtn commands={commands} button={RemoteButton.NextTrack} />
      </div>

      {/* Secondary row */}
      {hasSecondary && (
        <div className="transport-secondary-row">
          {showPause  && <TBtn commands={commands} button={RemoteButton.Pause} />}
          {showStop   && <TBtn commands={commands} button={RemoteButton.Stop} />}
          {showRecord && <TBtn commands={commands} button={RemoteButton.Record} />}
        </div>
      )}
    </div>
  );
}
