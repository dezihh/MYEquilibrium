export interface Scene {
  id: number;
  name: string;
  image_id: number | null;
  device_ids: number[];
  start_macro_id: number | null;
  stop_macro_id: number | null;
  bluetooth_address: string | null;
}

export interface SceneCreate {
  name: string;
  image_id?: number | null;
  device_ids?: number[];
  start_macro_id?: number | null;
  stop_macro_id?: number | null;
  bluetooth_address?: string | null;
}
