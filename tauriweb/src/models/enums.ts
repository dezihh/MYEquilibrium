export enum DeviceType {
  Display = 'display',
  Amplifier = 'amplifier',
  Player = 'player',
  Integration = 'integration',
  Other = 'other',
}

export const DeviceTypeLabel: Record<DeviceType, string> = {
  [DeviceType.Display]: 'Display',
  [DeviceType.Amplifier]: 'Verstärker',
  [DeviceType.Player]: 'Player',
  [DeviceType.Integration]: 'Integration',
  [DeviceType.Other]: 'Sonstiges',
};

export enum CommandType {
  Infrared = 'ir',
  Bluetooth = 'bluetooth',
  Network = 'network',
  Script = 'script',
  Integration = 'integration',
}

export const CommandTypeLabel: Record<CommandType, string> = {
  [CommandType.Infrared]: 'Infrarot',
  [CommandType.Bluetooth]: 'Bluetooth',
  [CommandType.Network]: 'Netzwerk',
  [CommandType.Script]: 'Shellscript',
  [CommandType.Integration]: 'Integration',
};

export enum CommandGroupType {
  Power = 'power',
  Volume = 'volume',
  Navigation = 'navigation',
  Transport = 'transport',
  Channel = 'channel',
  Numeric = 'numeric',
  Input = 'input',
  ColoredButtons = 'colored_buttons',
  Other = 'other',
}

export const CommandGroupTypeLabel: Record<CommandGroupType, string> = {
  [CommandGroupType.Power]: 'Power',
  [CommandGroupType.Volume]: 'Lautstärke',
  [CommandGroupType.Navigation]: 'Navigation',
  [CommandGroupType.Transport]: 'Transport',
  [CommandGroupType.Channel]: 'Kanal',
  [CommandGroupType.Numeric]: 'Nummern',
  [CommandGroupType.Input]: 'Eingang',
  [CommandGroupType.ColoredButtons]: 'Farbtasten',
  [CommandGroupType.Other]: 'Sonstiges',
};

export enum BluetoothCommandType {
  RegularKey = 'regular_key',
  MediaKey = 'media_key',
}

export const BluetoothCommandTypeLabel: Record<BluetoothCommandType, string> = {
  [BluetoothCommandType.RegularKey]: 'Taste',
  [BluetoothCommandType.MediaKey]: 'Medientaste',
};

export enum BluetoothCommand {
  Escape = 'escape',
  Enter = 'enter',
  Up = 'up',
  Down = 'down',
  Left = 'left',
  Right = 'right',
  Other = 'other',
  Play = 'play',
  Pause = 'pause',
  PlayPause = 'play_pause',
  FastForward = 'fast_forward',
  Rewind = 'rewind',
  NextTrack = 'next_track',
  PreviousTrack = 'previous_track',
  VolumeUp = 'volume_up',
  VolumeDown = 'volume_down',
  Mute = 'mute',
}

export const BluetoothCommandsByType: Record<BluetoothCommandType, BluetoothCommand[]> = {
  [BluetoothCommandType.RegularKey]: [
    BluetoothCommand.Escape, BluetoothCommand.Enter,
    BluetoothCommand.Up, BluetoothCommand.Down,
    BluetoothCommand.Left, BluetoothCommand.Right,
    BluetoothCommand.Other,
  ],
  [BluetoothCommandType.MediaKey]: [
    BluetoothCommand.Play, BluetoothCommand.Pause,
    BluetoothCommand.PlayPause, BluetoothCommand.FastForward,
    BluetoothCommand.Rewind, BluetoothCommand.NextTrack,
    BluetoothCommand.PreviousTrack, BluetoothCommand.VolumeUp,
    BluetoothCommand.VolumeDown, BluetoothCommand.Mute,
  ],
};

export enum NetworkRequestType {
  Get = 'get',
  Post = 'post',
  Patch = 'patch',
  Delete = 'delete',
  Head = 'head',
  Put = 'put',
}

export const NetworkRequestTypeCanHaveBody: Record<NetworkRequestType, boolean> = {
  [NetworkRequestType.Get]: false,
  [NetworkRequestType.Head]: false,
  [NetworkRequestType.Delete]: false,
  [NetworkRequestType.Post]: true,
  [NetworkRequestType.Patch]: true,
  [NetworkRequestType.Put]: true,
};

export enum IntegrationAction {
  ToggleLight = 'toggle_light',
  TurnOn = 'turn_on',
  TurnOff = 'turn_off',
  BrightnessUp = 'brightness_up',
  BrightnessDown = 'brightness_down',
  CallService = 'call_service',
}

export const IntegrationActionLabel: Record<IntegrationAction, string> = {
  [IntegrationAction.ToggleLight]: 'Toggle',
  [IntegrationAction.TurnOn]: 'Turn on',
  [IntegrationAction.TurnOff]: 'Turn off',
  [IntegrationAction.BrightnessUp]: 'Helligkeit erhöhen',
  [IntegrationAction.BrightnessDown]: 'Helligkeit verringern',
  [IntegrationAction.CallService]: 'Service Call',
};

export enum RemoteButton {
  // Power
  PowerToggle = 'power_toggle',
  PowerOff = 'power_off',
  PowerOn = 'power_on',
  // Volume
  VolumeUp = 'volume_up',
  VolumeDown = 'volume_down',
  Mute = 'mute',
  // Navigation
  DirectionUp = 'direction_up',
  DirectionDown = 'direction_down',
  DirectionLeft = 'direction_left',
  DirectionRight = 'direction_right',
  Select = 'select',
  Guide = 'guide',
  Info = 'info',
  Back = 'back',
  Menu = 'menu',
  Home = 'home',
  Exit = 'exit',
  // Transport
  Play = 'play',
  Pause = 'pause',
  PlayPause = 'playpause',
  Stop = 'stop',
  FastForward = 'fast_forward',
  Rewind = 'rewind',
  NextTrack = 'next_track',
  PreviousTrack = 'previous_track',
  Record = 'record',
  // Channel
  ChannelUp = 'channel_up',
  ChannelDown = 'channel_down',
  // Colored Buttons
  Green = 'green',
  Red = 'red',
  Blue = 'blue',
  Yellow = 'yellow',
  // Numeric
  Number0 = 'number_zero',
  Number1 = 'number_one',
  Number2 = 'number_two',
  Number3 = 'number_three',
  Number4 = 'number_four',
  Number5 = 'number_five',
  Number6 = 'number_six',
  Number7 = 'number_seven',
  Number8 = 'number_eight',
  Number9 = 'number_nine',
  // Other
  BrightnessUp = 'brightness_up',
  BrightnessDown = 'brightness_down',
  TurnOn = 'turn_on',
  TurnOff = 'turn_off',
  Other = 'other',
}

export const RemoteButtonsByGroup: Record<CommandGroupType, RemoteButton[]> = {
  [CommandGroupType.Power]: [RemoteButton.PowerToggle, RemoteButton.PowerOn, RemoteButton.PowerOff],
  [CommandGroupType.Volume]: [RemoteButton.VolumeUp, RemoteButton.VolumeDown, RemoteButton.Mute],
  [CommandGroupType.Navigation]: [
    RemoteButton.DirectionUp, RemoteButton.DirectionDown, RemoteButton.DirectionLeft, RemoteButton.DirectionRight,
    RemoteButton.Select, RemoteButton.Back, RemoteButton.Menu, RemoteButton.Home, RemoteButton.Exit, RemoteButton.Guide, RemoteButton.Info,
  ],
  [CommandGroupType.Transport]: [
    RemoteButton.Play, RemoteButton.Pause, RemoteButton.PlayPause, RemoteButton.Stop,
    RemoteButton.FastForward, RemoteButton.Rewind, RemoteButton.NextTrack, RemoteButton.PreviousTrack, RemoteButton.Record,
  ],
  [CommandGroupType.Channel]: [RemoteButton.ChannelUp, RemoteButton.ChannelDown],
  [CommandGroupType.Numeric]: [
    RemoteButton.Number0, RemoteButton.Number1, RemoteButton.Number2,
    RemoteButton.Number3, RemoteButton.Number4, RemoteButton.Number5,
    RemoteButton.Number6, RemoteButton.Number7, RemoteButton.Number8, RemoteButton.Number9,
  ],
  [CommandGroupType.Input]: [RemoteButton.Other],
  [CommandGroupType.ColoredButtons]: [RemoteButton.Red, RemoteButton.Green, RemoteButton.Yellow, RemoteButton.Blue],
  [CommandGroupType.Other]: [RemoteButton.BrightnessUp, RemoteButton.BrightnessDown, RemoteButton.TurnOn, RemoteButton.TurnOff, RemoteButton.Other],
};
