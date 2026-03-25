import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

const hasBtn = (commands: Command[], btn: RemoteButton) =>
  commands.some(c => c.button === btn);

// Blüten-D-Pad: Pills überlappen sich physisch in der Mitte, OK liegt obendrauf.
// Eckbuttons (Back/Exit/Home/Menu) sitzen absolut in den vier Ecken.
export default function NavigationDPadGroup({ commands }: Props) {
  const hasExtras = hasBtn(commands, RemoteButton.Guide) || hasBtn(commands, RemoteButton.Info);

  return (
    <div className="nav-dpad-wrap">
      <div className="nav-dpad-outer">

        {/* ── Ecken ── */}
        <div className="nav-corner nav-tl">
          <CommandButtonIfExists commands={commands} button={RemoteButton.Back} />
        </div>
        <div className="nav-corner nav-tr">
          <CommandButtonIfExists commands={commands} button={RemoteButton.Exit} />
        </div>
        <div className="nav-corner nav-bl">
          <CommandButtonIfExists commands={commands} button={RemoteButton.Home} />
        </div>
        <div className="nav-corner nav-br">
          <CommandButtonIfExists commands={commands} button={RemoteButton.Menu} />
        </div>

        {/* ── Pills direkt im Outer positioniert ── */}
        <div className="nav-dir nav-up">
          <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionUp} />
        </div>
        <div className="nav-dir nav-left">
          <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionLeft} />
        </div>
        <div className="nav-dir nav-right">
          <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionRight} />
        </div>
        <div className="nav-dir nav-down">
          <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionDown} />
        </div>
        {/* OK liegt mit z-index 2 über den Pills */}
        <div className="nav-ok">
          <CommandButtonIfExists commands={commands} button={RemoteButton.Select} primary />
        </div>

      </div>

      {/* Guide / Info optional */}
      {hasExtras && (
        <div className="nav-extras-row">
          {hasBtn(commands, RemoteButton.Guide) && (
            <CommandButtonIfExists commands={commands} button={RemoteButton.Guide} />
          )}
          {hasBtn(commands, RemoteButton.Info) && (
            <CommandButtonIfExists commands={commands} button={RemoteButton.Info} />
          )}
        </div>
      )}
    </div>
  );
}
