export interface Macro {
  id: number;
  name: string;
  command_ids: number[];
  delays: number[];
}

export interface MacroCreate {
  name: string;
  command_ids?: number[];
  delays?: number[];
}
