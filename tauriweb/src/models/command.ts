import { RemoteButton, CommandType, CommandGroupType } from './enums';

export interface Command {
  id: number;
  name: string;
  button: RemoteButton;
  type: CommandType;
  command_group: CommandGroupType;
  device_id: number | null;
  host: string | null;
  method: string | null;
  body: string | null;
  bt_action: string | null;
  bt_media_action: string | null;
  integration_action: string | null;
  integration_entity: string | null;
}

export interface CommandCreate {
  name: string;
  button: RemoteButton;
  type: CommandType;
  command_group: CommandGroupType;
  device_id: number | null;
  host?: string | null;
  method?: string | null;
  body?: string | null;
  bt_action?: string | null;
  bt_media_action?: string | null;
  integration_action?: string | null;
  integration_entity?: string | null;
}
