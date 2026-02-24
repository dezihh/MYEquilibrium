export interface Scene {
  id: number;
  name: string;
  imageId: number | null;
  devices: number[];
  startMacro: number | null;
  stopMacro: number | null;
}

export interface SceneCreate {
  name: string;
  imageId?: number | null;
  devices?: number[];
  startMacro?: number | null;
  stopMacro?: number | null;
}
