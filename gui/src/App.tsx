import { useEffect, useMemo, useRef, useState } from "react";
import { ConnectPage } from "./pages/ConnectPage";
import { CommandEditPage, type CommandDraft } from "./pages/CommandEditPage";
import { CommandsPage } from "./pages/CommandsPage";
import { DevicesPage } from "./pages/DevicesPage";
import { IconsPage } from "./pages/IconsPage";
import { ScenesPage } from "./pages/ScenesPage";
import { SettingsPage } from "./pages/SettingsPage";
import { useMenuState } from "./hooks/useMenuState";
import type {
  Command,
  CommandDetail,
  Device,
  Scene,
  SettingItem,
  SettingsView,
  TabKey,
  UserImage,
} from "./types";

const defaultScenes: Scene[] = [
  {
    id: 1,
    name: "FirstScene",
    devices: ["Nokia1"],
    status: "inactive",
  },
  {
    id: 2,
    name: "Movie Night",
    devices: ["Projector", "AVR", "Blu-ray"],
    status: "inactive",
  },
];

const defaultDevices: Device[] = [
  {
    id: 1,
    name: "LG OLED",
    model: "C2",
    category: "Display",
  },
  {
    id: 2,
    name: "Denon AVR",
    model: "X2700H",
    category: "Amplifier",
  },
  {
    id: 3,
    name: "Chromecast",
    category: "Player",
  },
];

const settingsItems: SettingItem[] = [
  {
    id: "icons",
    title: "Icons",
    icon: "image",
  },
  {
    id: "bluetooth",
    title: "Bluetooth Devices",
    icon: "bluetooth",
  },
  {
    id: "commands",
    title: "Commands",
    icon: "code",
  },
  {
    id: "macros",
    title: "Macros",
    icon: "macro",
  },
];

const STORAGE_KEY = "equilibrium_hub_url";


export default function App() {
  const [hubUrl, setHubUrl] = useState(
    () => window.localStorage.getItem(STORAGE_KEY) || ""
  );
  const [connected, setConnected] = useState(Boolean(hubUrl));
  const [activeTab, setActiveTab] = useState<TabKey>("scenes");
  const [scenes, setScenes] = useState<Scene[]>(defaultScenes);
  const [devices, setDevices] = useState<Device[]>(defaultDevices);
  const [invertImages, setInvertImages] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [settingsView, setSettingsView] = useState<SettingsView>("root");
  const [images, setImages] = useState<UserImage[]>([]);
  const [imagesLoading, setImagesLoading] = useState(false);
  const [imagesError, setImagesError] = useState<string | null>(null);
  const [commands, setCommands] = useState<Command[]>([]);
  const [commandsLoading, setCommandsLoading] = useState(false);
  const [commandsError, setCommandsError] = useState<string | null>(null);
  const [commandEdit, setCommandEdit] = useState<CommandDetail | null>(null);
  const [commandEditLoading, setCommandEditLoading] = useState(false);
  const [commandEditLoadError, setCommandEditLoadError] = useState<
    string | null
  >(null);
  const [commandEditSaveError, setCommandEditSaveError] = useState<
    string | null
  >(null);
  const [editingCommandId, setEditingCommandId] = useState<number | null>(null);
  const [deviceOptions, setDeviceOptions] = useState<Device[]>([]);
  const [deviceOptionsError, setDeviceOptionsError] = useState<string | null>(
    null
  );
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const imageMenu = useMenuState<number>();
  const commandsMenu = useMenuState<number>();

  const activeScene = useMemo(
    () => scenes.find((scene) => scene.status === "active"),
    [scenes]
  );

  const handleConnect = () => {
    if (!hubUrl.trim()) return;
    window.localStorage.setItem(STORAGE_KEY, hubUrl.trim());
    setConnected(true);
  };

  const toggleScene = (sceneId: number) => {
    setScenes((prev) =>
      prev.map((scene) => {
        if (scene.id !== sceneId) {
          return { ...scene, status: "inactive" };
        }
        const nextStatus = scene.status === "active" ? "inactive" : "active";
        return { ...scene, status: nextStatus };
      })
    );
  };

  const addScene = () => {
    setScenes((prev) => {
      const nextId = prev.length ? Math.max(...prev.map((s) => s.id)) + 1 : 1;
      return [
        ...prev,
        {
          id: nextId,
          name: `New Scene ${nextId}`,
          devices: ["New Device"],
          status: "inactive",
        },
      ];
    });
  };

  const addDevice = () => {
    setDevices((prev) => {
      const nextId = prev.length ? Math.max(...prev.map((d) => d.id)) + 1 : 1;
      return [
        ...prev,
        {
          id: nextId,
          name: `New Device ${nextId}`,
          category: "Other",
        },
      ];
    });
  };

  const fetchImages = async () => {
    setImagesLoading(true);
    setImagesError(null);
    try {
      const response = await fetch("/images/");
      if (!response.ok) {
        throw new Error(`Failed to load images (${response.status})`);
      }
      const data = (await response.json()) as UserImage[];
      setImages(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setImagesError(message);
    } finally {
      setImagesLoading(false);
    }
  };

  const fetchCommandDetail = async (commandId: number) => {
    setCommandEditLoading(true);
    setCommandEditLoadError(null);
    try {
      const response = await fetch(`/commands/${commandId}`);
      if (!response.ok) {
        throw new Error(`Failed to load command (${response.status})`);
      }
      const data = (await response.json()) as CommandDetail;
      setCommandEdit(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCommandEditLoadError(message);
    } finally {
      setCommandEditLoading(false);
    }
  };

  const fetchDeviceOptions = async () => {
    setDeviceOptionsError(null);
    try {
      const response = await fetch("/devices/");
      if (!response.ok) {
        throw new Error(`Failed to load devices (${response.status})`);
      }
      const data = (await response.json()) as Device[];
      setDeviceOptions(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setDeviceOptionsError(message);
    }
  };

  const fetchCommands = async () => {
    setCommandsLoading(true);
    setCommandsError(null);
    try {
      const response = await fetch("/commands/");
      if (!response.ok) {
        throw new Error(`Failed to load commands (${response.status})`);
      }
      const data = (await response.json()) as Command[];
      setCommands(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCommandsError(message);
    } finally {
      setCommandsLoading(false);
    }
  };
  const toErrorMessage = (error: unknown, fallback: string) =>
    error instanceof Error ? error.message : fallback;

  const uploadImage = async (file: File) => {
    setImagesError(null);
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await fetch("/images/", {
        method: "POST",
        body,
      });
      if (!response.ok) {
        throw new Error(`Upload failed (${response.status})`);
      }
      await fetchImages();
    } catch (error) {
      setImagesError(toErrorMessage(error, "Upload failed"));
    }
  };

  const deleteImage = async (imageId: number) => {
    setImagesError(null);
    try {
      const response = await fetch(`/images/${imageId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(`Delete failed (${response.status})`);
      }
      await fetchImages();
    } catch (error) {
      setImagesError(toErrorMessage(error, "Delete failed"));
    }
  };

  const renameImage = async (imageId: number, filename: string) => {
    setImagesError(null);
    try {
      const response = await fetch(`/images/${imageId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename }),
      });
      if (!response.ok) {
        throw new Error(`Rename failed (${response.status})`);
      }
      await fetchImages();
    } catch (error) {
      setImagesError(toErrorMessage(error, "Rename failed"));
    }
  };

  const sendCommand = async (commandId: number) => {
    setCommandsError(null);
    try {
      const response = await fetch(`/commands/${commandId}/send`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`Send failed (${response.status})`);
      }
    } catch (error) {
      setCommandsError(toErrorMessage(error, "Send failed"));
    }
  };

  const deleteCommand = async (commandId: number) => {
    setCommandsError(null);
    try {
      const response = await fetch(`/commands/${commandId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(`Delete failed (${response.status})`);
      }
      await fetchCommands();
    } catch (error) {
      setCommandsError(toErrorMessage(error, "Delete failed"));
    }
  };

  const buildCommandPayload = (draft: CommandDraft) => {
    const isNetwork = draft.type === "network";
    const isBluetooth = draft.type === "bluetooth";
    const isIntegration = draft.type === "integration";
    return {
      name: draft.name,
      device_id: draft.device_id,
      command_group: draft.command_group,
      type: draft.type,
      button: draft.button,
      host: isNetwork ? draft.host : null,
      method: isNetwork ? draft.method : null,
      body: isNetwork ? draft.body : null,
      bt_action:
        isBluetooth && draft.bt_key_type === "regular" ? draft.bt_key : null,
      bt_media_action:
        isBluetooth && draft.bt_key_type === "media" ? draft.bt_key : null,
      integration_action: isIntegration ? draft.integration_action : null,
      integration_entity: isIntegration ? draft.integration_entity : null,
    };
  };

  const saveEditedCommand = async (draft: CommandDraft) => {
    if (draft.type === "ir") {
      setCommandEditSaveError(
        "Infrared commands can only be learned via WebSocket right now."
      );
      return;
    }
    if (draft.type === "script") {
      setCommandEditSaveError("Script commands are not supported yet.");
      return;
    }
    setCommandEditSaveError(null);
    try {
      const payload = buildCommandPayload(draft);
      const createResponse = await fetch("/commands/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!createResponse.ok) {
        throw new Error(`Create failed (${createResponse.status})`);
      }

      if (editingCommandId !== null) {
        const deleteResponse = await fetch(`/commands/${editingCommandId}`, {
          method: "DELETE",
        });
        if (!deleteResponse.ok) {
          throw new Error(`Delete failed (${deleteResponse.status})`);
        }
      }

      await fetchCommands();
      setSettingsView("commands");
      setEditingCommandId(null);
    } catch (error) {
      setCommandEditSaveError(toErrorMessage(error, "Save failed"));
    }
  };

  const renderSettings = () =>
    settingsView === "icons" ? (
      <IconsPage
        images={images}
        loading={imagesLoading}
        error={imagesError}
        openMenuId={imageMenu.openId}
        onToggleMenu={imageMenu.toggle}
        onCloseMenu={imageMenu.close}
        onRename={renameImage}
        onDelete={deleteImage}
        onUpload={uploadImage}
        onBack={() => setSettingsView("root")}
        imageInputRef={imageInputRef}
      />
    ) : settingsView === "commands" ? (
      <CommandsPage
        commands={commands}
        loading={commandsLoading}
        error={commandsError}
        openMenuId={commandsMenu.openId}
        onToggleMenu={commandsMenu.toggle}
        onCloseMenu={commandsMenu.close}
        onSend={sendCommand}
        onDelete={deleteCommand}
        onEdit={(commandId) => {
          setCommandEdit(null);
          setCommandEditLoadError(null);
          setCommandEditSaveError(null);
          setEditingCommandId(commandId);
          setSettingsView("command-edit");
        }}
        onCreate={() => {
          setCommandEdit(null);
          setCommandEditLoadError(null);
          setCommandEditSaveError(null);
          setEditingCommandId(null);
          setSettingsView("command-edit");
        }}
        onBack={() => setSettingsView("root")}
      />
    ) : settingsView === "command-edit" ? (
      <CommandEditPage
        title={editingCommandId === null ? "New Command" : "Edit Command"}
        command={commandEdit}
        devices={deviceOptions}
        loading={commandEditLoading}
        loadError={commandEditLoadError}
        saveError={commandEditSaveError}
        deviceError={deviceOptionsError}
        onSave={saveEditedCommand}
        onCancel={() => {
          setSettingsView("commands");
          setEditingCommandId(null);
        }}
      />
    ) : (
      <SettingsPage
        items={settingsItems}
        invertImages={invertImages}
        darkMode={darkMode}
        onToggleInvert={() => setInvertImages((prev) => !prev)}
        onToggleDarkMode={() => setDarkMode((prev) => !prev)}
        onSelectItem={(id) => {
          if (id === "icons") {
            setSettingsView("icons");
            return;
          }
          if (id === "commands") {
            setSettingsView("commands");
          }
        }}
      />
    );

  useEffect(() => {
    if (settingsView === "icons") {
      fetchImages();
    }
    if (settingsView === "commands") {
      fetchCommands();
    }
    if (settingsView === "command-edit") {
      if (editingCommandId !== null) {
        fetchCommandDetail(editingCommandId);
      }
      fetchDeviceOptions();
    }
  }, [settingsView, editingCommandId]);

  return (
    <div className={`app ${darkMode ? "app--dark" : "app--light"}`}>
      <div className="app__glow" aria-hidden="true" />
      <main className="app__frame">
        {!connected ? (
          <ConnectPage
            hubUrl={hubUrl}
            onHubUrlChange={setHubUrl}
            onConnect={handleConnect}
          />
        ) : activeTab === "scenes" ? (
          <ScenesPage
            scenes={scenes}
            activeScene={activeScene}
            onAddScene={addScene}
            onToggleScene={toggleScene}
          />
        ) : activeTab === "devices" ? (
          <DevicesPage devices={devices} onAddDevice={addDevice} />
        ) : (
          renderSettings()
        )}
      </main>

      <nav className="bottom-nav" aria-label="Primary">
        <button
          className={`bottom-nav__item ${
            activeTab === "scenes" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("scenes")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">▣</span>
          Scenes
        </button>
        <button
          className={`bottom-nav__item ${
            activeTab === "devices" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("devices")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">▢</span>
          Devices
        </button>
        <button
          className={`bottom-nav__item ${
            activeTab === "settings" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("settings")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">⚙</span>
          Settings
        </button>
      </nav>
    </div>
  );
}
