import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

// D-Pad: 3×3 Grid, Ecken leer — reines Richtungskreuz mit OK in der Mitte
export default function DPadControlGroup({ commands }: Props) {
  return (
    <div className="dpad-grid">
      {/* Row 1 */}
      <span />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionUp} />
      <span />
      {/* Row 2 */}
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionLeft} />
      <CommandButtonIfExists commands={commands} button={RemoteButton.Select} primary />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionRight} />
      {/* Row 3 */}
      <span />
      <CommandButtonIfExists commands={commands} button={RemoteButton.DirectionDown} />
      <span />
    </div>
  );
}
