import { Command } from '../../models/command';
import { RemoteButton } from '../../models/enums';
import CommandButtonIfExists from './CommandButtonIfExists';

interface Props { commands: Command[]; }

const SOFT_KEYS = [
  RemoteButton.Back,
  RemoteButton.Home,
  RemoteButton.Menu,
  RemoteButton.Exit,
  RemoteButton.Guide,
  RemoteButton.Info,
];

// Soft-Keys: Flex-Reihe mit Back/Home/Menu/Exit/Guide/Info
export default function SoftKeysControlGroup({ commands }: Props) {
  const present = SOFT_KEYS.filter(btn =>
    commands.some(c => c.button === btn)
  );

  if (present.length === 0) return null;

  return (
    <div className="softkeys-row">
      {present.map(btn => (
        <CommandButtonIfExists key={btn} commands={commands} button={btn} />
      ))}
    </div>
  );
}
