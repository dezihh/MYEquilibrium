import { IconButton } from "../components/Button";
import { getCommandIcon } from "../components/commandIcons";
import { getButtonLabel, getGroupLabel, getTypeLabel } from "../constants/commandOptions";
import { ListRow } from "../components/ListRow";
import { Menu, MenuAnchor, MenuItem } from "../components/Menu";
import { PageEmpty, PageHeader } from "../components/Page";
import type { Command } from "../types";

export type CommandsPageProps = {
  commands: Command[];
  loading: boolean;
  error: string | null;
  openMenuId: number | null;
  onToggleMenu: (commandId: number) => void;
  onCloseMenu: () => void;
  onSend: (commandId: number) => Promise<void>;
  onDelete: (commandId: number) => Promise<void>;
  onEdit: (commandId: number) => void;
  onCreate: () => void;
  onBack: () => void;
};

export const CommandsPage = ({
  commands,
  loading,
  error,
  openMenuId,
  onToggleMenu,
  onCloseMenu,
  onSend,
  onDelete,
  onEdit,
  onCreate,
  onBack,
}: CommandsPageProps) => (
  <section className="page">
    <PageHeader title="Commands" onBack={onBack} />

    {loading ? (
      <PageEmpty>Loading commands...</PageEmpty>
    ) : error ? (
      <PageEmpty>{error}</PageEmpty>
    ) : commands.length === 0 ? (
      <PageEmpty>No commands configured yet.</PageEmpty>
    ) : (
      <div className="list list--menu">
        {commands.map((command) => (
          <ListRow
            key={command.id}
            leading={
              <div className="list-row__icon">
                {getCommandIcon(command.button) ?? command.name.slice(0, 1)}
              </div>
            }
            title={command.name}
            subtitle={`${getTypeLabel(command.type)} • ${getGroupLabel(
              command.command_group
            )} • ${getButtonLabel(command.command_group, command.button)}`}
            actions={
              <MenuAnchor>
                <IconButton
                  aria-label="Command menu"
                  aria-expanded={openMenuId === command.id}
                  onClick={() => onToggleMenu(command.id)}
                >
                  <span>•••</span>
                </IconButton>
                {openMenuId === command.id && (
                  <Menu>
                    <MenuItem
                      onClick={async () => {
                        await onSend(command.id);
                        onCloseMenu();
                      }}
                    >
                      Senden
                    </MenuItem>
                    <MenuItem
                      onClick={() => {
                        onEdit(command.id);
                        onCloseMenu();
                      }}
                    >
                      Edit
                    </MenuItem>
                    <MenuItem
                      tone="danger"
                      onClick={async () => {
                        await onDelete(command.id);
                        onCloseMenu();
                      }}
                    >
                      Delete
                    </MenuItem>
                  </Menu>
                )}
              </MenuAnchor>
            }
          />
        ))}
      </div>
    )}

    <button className="fab" aria-label="Add command" onClick={onCreate}>
      +
    </button>
  </section>
);
