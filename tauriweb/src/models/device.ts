import { Command } from './command';
import { DeviceType } from './enums';

export interface Device {
  id: number;
  name: string;
  type: DeviceType;
  commands: Command[];
}

export interface DeviceCreate {
  name: string;
  type: DeviceType;
}
