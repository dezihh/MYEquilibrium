import { Command } from './command';
import { DeviceType } from './enums';

export interface Device {
  id: number;
  name: string;
  type: DeviceType;
  manufacturer: string | null;
  model: string | null;
  image_id: number | null;
  bluetooth_address: string | null;
  commands: Command[];
}

export interface DeviceCreate {
  name: string;
  type: DeviceType;
  manufacturer?: string | null;
  model?: string | null;
  image_id?: number | null;
  bluetooth_address?: string | null;
}
