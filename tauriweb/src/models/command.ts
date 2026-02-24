import { RemoteButton } from './enums';

export interface Command {
  id: number;
  name: string;
  button: RemoteButton;
  code: string;
  deviceId: number;
}

export interface CommandCreate {
  name: string;
  button: RemoteButton;
  deviceId: number;
}
