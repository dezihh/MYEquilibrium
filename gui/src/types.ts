export type SceneStatus = "active" | "inactive" | "starting" | "stopping";
export type TabKey = "scenes" | "devices" | "settings";
export type SettingsView = "root" | "icons" | "commands" | "command-edit";

export type Scene = {
  id: number;
  name: string;
  devices: string[];
  status: SceneStatus;
};

export type Device = {
  id: number;
  name: string;
  model?: string;
  category: string;
};

export type UserImage = {
  id: number;
  filename: string;
  path: string;
};

export type SettingItem = {
  id: string;
  title: string;
  description?: string;
  icon: "image" | "bluetooth" | "code" | "macro" | "invert";
};

export type Command = {
  id: number;
  name: string;
  type: string;
  command_group: string;
  button: string;
  device_id?: number | null;
};

export type CommandDetail = Command & {
  host?: string | null;
  method?: string | null;
  body?: string | null;
  bt_action?: string | null;
  bt_media_action?: string | null;
  integration_action?: string | null;
  integration_entity?: string | null;
};
