export interface MacroStep {
  deviceId: number;
  commandId: number;
  delay: number;
}

export interface Macro {
  id: number;
  name: string;
  steps: MacroStep[];
}

export interface MacroCreate {
  name: string;
  steps?: MacroStep[];
}
