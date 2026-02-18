import { useEffect, useMemo, useState } from "react";
import { Button } from "../components/Button";
import { PageEmpty, PageHeader } from "../components/Page";
import { SelectMenu } from "../components/SelectMenu";
import { getCommandIcon } from "../components/commandIcons";
import type { CommandDetail, Device } from "../types";
import {
  bluetoothKeyOptions,
  bluetoothKeyTypeOptions,
  bluetoothMediaKeyOptions,
  commandGroupOptions,
  commandTypeOptions,
  getButtonOptions,
  integrationActionOptions,
  networkMethodOptions,
} from "../constants/commandOptions";

export type CommandDraft = {
  name: string;
  device_id: number | null;
  command_group: string;
  type: string;
  button: string;
  host: string;
  method: string;
  body: string;
  bt_key_type: "regular" | "media";
  bt_key: string;
  integration_action: string;
  integration_entity: string;
};

export type CommandEditPageProps = {
  title: string;
  command: CommandDetail | null;
  devices: Device[];
  loading: boolean;
  loadError: string | null;
  saveError: string | null;
  deviceError: string | null;
  onSave: (draft: CommandDraft) => Promise<void>;
  onCancel: () => void;
};

const emptyDraft: CommandDraft = {
  name: "",
  device_id: null,
  command_group: "other",
  type: "ir",
  button: "other",
  host: "",
  method: "get",
  body: "",
  bt_key_type: "regular",
  bt_key: "KEY_ESC",
  integration_action: "toggle_light",
  integration_entity: "",
};

const normalizeButton = (group: string, button: string) => {
  const options = getButtonOptions(group);
  if (options.some((option) => option.value === button)) {
    return button;
  }
  return options[0]?.value ?? "other";
};

const buildDraftFromCommand = (command: CommandDetail | null): CommandDraft => {
  if (!command) return emptyDraft;

  const isMedia = Boolean(command.bt_media_action);
  const group = command.command_group ?? "other";
  const button = normalizeButton(group, command.button ?? "other");
  return {
    name: command.name ?? "",
    device_id: command.device_id ?? null,
    command_group: group,
    type: command.type ?? "ir",
    button,
    host: command.host ?? "",
    method: command.method ?? "get",
    body: command.body ?? "",
    bt_key_type: isMedia ? "media" : "regular",
    bt_key: isMedia
      ? command.bt_media_action ?? "KEY_PLAY"
      : command.bt_action ?? "KEY_ESC",
    integration_action: command.integration_action ?? "toggle_light",
    integration_entity: command.integration_entity ?? "",
  };
};

export const CommandEditPage = ({
  title,
  command,
  devices,
  loading,
  loadError,
  saveError,
  deviceError,
  onSave,
  onCancel,
}: CommandEditPageProps) => {
  const [draft, setDraft] = useState<CommandDraft>(emptyDraft);
  const [saving, setSaving] = useState(false);
  const [localSaveError, setLocalSaveError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(buildDraftFromCommand(command));
  }, [command]);

  const keyOptions = useMemo(
    () =>
      draft.bt_key_type === "media"
        ? bluetoothMediaKeyOptions
        : bluetoothKeyOptions,
    [draft.bt_key_type]
  );

  const buttonOptions = useMemo(
    () => getButtonOptions(draft.command_group),
    [draft.command_group]
  );

  const buttonOptionsWithIcons = useMemo(
    () =>
      buttonOptions.map((option) => ({
        ...option,
        icon: getCommandIcon(option.value),
      })),
    [buttonOptions]
  );

  useEffect(() => {
    if (!buttonOptions.some((option) => option.value === draft.button)) {
      setDraft((current) => ({
        ...current,
        button: buttonOptions[0]?.value ?? "other",
      }));
    }
  }, [buttonOptions, draft.button]);

  const requiresEntity =
    draft.type === "integration" && draft.integration_action === "toggle_light";

  const isSaveDisabled =
    !draft.name.trim() ||
    !draft.command_group ||
    !draft.type ||
    !draft.button ||
    (draft.type === "network" && (!draft.host.trim() || !draft.method)) ||
    (draft.type === "bluetooth" && !draft.bt_key) ||
    (requiresEntity && !draft.integration_entity.trim()) ||
    draft.type === "ir" ||
    draft.type === "script";

  const handleSave = async () => {
    setLocalSaveError(null);
    setSaving(true);
    try {
      await onSave(draft);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Save failed";
      setLocalSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page">
      <PageHeader title={title} onBack={onCancel} />

      {loading ? (
        <PageEmpty>Loading command...</PageEmpty>
      ) : loadError ? (
        <PageEmpty>{loadError}</PageEmpty>
      ) : (
        <div className="form">
          <div className="form-field">
            <label className="form-label" htmlFor="command-name">
              Name
            </label>
            <input
              id="command-name"
              className="form-control"
              value={draft.name}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
            />
          </div>

          <div className="form-field">
            <label className="form-label" htmlFor="command-device">
              Device
            </label>
            <select
              id="command-device"
              className="form-control"
              value={draft.device_id ?? ""}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  device_id: event.target.value
                    ? Number(event.target.value)
                    : null,
                }))
              }
            >
              <option value="">None</option>
              {devices.map((device) => (
                <option key={device.id} value={device.id}>
                  {device.name}
                </option>
              ))}
            </select>
            {deviceError ? (
              <div className="form-note form-note--warn">{deviceError}</div>
            ) : null}
          </div>

          <div className="form-field">
            <SelectMenu
              id="command-group"
              label="Command group"
              value={draft.command_group}
              options={commandGroupOptions}
              onChange={(nextGroup) => {
                const nextButtons = getButtonOptions(nextGroup);
                setDraft((current) => ({
                  ...current,
                  command_group: nextGroup,
                  button: nextButtons[0]?.value ?? "other",
                }));
              }}
            />
          </div>

          <div className="form-field">
            <SelectMenu
              id="command-type"
              label="Type"
              value={draft.type}
              options={commandTypeOptions}
              onChange={(nextType) =>
                setDraft((current) => ({
                  ...current,
                  type: nextType,
                }))
              }
            />
          </div>

          <div className="form-field">
            <SelectMenu
              id="command-button"
              label="Button type"
              value={draft.button}
              options={buttonOptionsWithIcons}
              onChange={(nextButton) =>
                setDraft((current) => ({
                  ...current,
                  button: nextButton,
                }))
              }
            />
          </div>

          {draft.type === "bluetooth" && (
            <>
              <div className="form-field">
                <label className="form-label" htmlFor="command-key-type">
                  Key Type
                </label>
                <select
                  id="command-key-type"
                  className="form-control"
                  value={draft.bt_key_type}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      bt_key_type: event.target.value as "regular" | "media",
                    }))
                  }
                >
                  {bluetoothKeyTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label className="form-label" htmlFor="command-key">
                  Key
                </label>
                <select
                  id="command-key"
                  className="form-control"
                  value={draft.bt_key}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      bt_key: event.target.value,
                    }))
                  }
                >
                  {keyOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {draft.type === "network" && (
            <>
              <div className="form-field">
                <label className="form-label" htmlFor="command-host">
                  Host
                </label>
                <input
                  id="command-host"
                  className="form-control"
                  value={draft.host}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      host: event.target.value,
                    }))
                  }
                />
              </div>
              <div className="form-field">
                <label className="form-label" htmlFor="command-method">
                  Method
                </label>
                <select
                  id="command-method"
                  className="form-control"
                  value={draft.method}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      method: event.target.value,
                    }))
                  }
                >
                  {networkMethodOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label className="form-label" htmlFor="command-body">
                  Body (optional)
                </label>
                <textarea
                  id="command-body"
                  className="form-control form-textarea"
                  value={draft.body}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      body: event.target.value,
                    }))
                  }
                  rows={4}
                />
              </div>
            </>
          )}

          {draft.type === "integration" && (
            <>
              <div className="form-field">
                <label className="form-label" htmlFor="command-action">
                  Action
                </label>
                <select
                  id="command-action"
                  className="form-control"
                  value={draft.integration_action}
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      integration_action: event.target.value,
                    }))
                  }
                >
                  {integrationActionOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              {requiresEntity && (
                <div className="form-field">
                  <label className="form-label" htmlFor="command-entity">
                    Entity
                  </label>
                  <input
                    id="command-entity"
                    className="form-control"
                    value={draft.integration_entity}
                    onChange={(event) =>
                      setDraft((current) => ({
                        ...current,
                        integration_entity: event.target.value,
                      }))
                    }
                  />
                </div>
              )}
            </>
          )}

          {draft.type === "ir" && (
            <>
              <div className="form-field">
                <Button variant="text" disabled>
                  Start learning command
                </Button>
              </div>
              <div className="form-note form-note--warn">
                Infrared commands can only be learned via WebSocket right now.
              </div>
            </>
          )}

          {draft.type === "script" && (
            <div className="form-note form-note--warn">
              Script commands are not supported yet.
            </div>
          )}

          {saveError || localSaveError ? (
            <div className="form-note form-note--warn">
              {saveError ?? localSaveError}
            </div>
          ) : null}

          <div className="form-actions">
            <Button variant="outline" onClick={onCancel} disabled={saving}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={saving || isSaveDisabled}
            >
              {saving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      )}
    </section>
  );
};
