import React from 'react';
import {
  Power, PowerOff, Zap,
  Volume2, Volume1, VolumeX,
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight,
  CornerDownLeft, Undo2, Home, Menu, X, LayoutGrid, Info,
  Play, Pause, PlayCircle, Square, FastForward, Rewind,
  SkipForward, SkipBack, Circle, Disc,
  Sun, SunDim,
} from 'lucide-react';
import { RemoteButton } from '../../models/enums';

const SIZE = 18;

// Maps RemoteButton → Lucide icon element
export const BUTTON_LUCIDE_ICONS: Partial<Record<RemoteButton, React.ReactElement>> = {
  // Power
  [RemoteButton.PowerToggle]: <Power size={SIZE} />,
  [RemoteButton.PowerOn]:     <Zap size={SIZE} />,
  [RemoteButton.PowerOff]:    <PowerOff size={SIZE} />,
  // Volume
  [RemoteButton.VolumeUp]:   <Volume2 size={SIZE} />,
  [RemoteButton.VolumeDown]: <Volume1 size={SIZE} />,
  [RemoteButton.Mute]:       <VolumeX size={SIZE} />,
  // Navigation
  [RemoteButton.DirectionUp]:    <ChevronUp    size={SIZE} />,
  [RemoteButton.DirectionDown]:  <ChevronDown  size={SIZE} />,
  [RemoteButton.DirectionLeft]:  <ChevronLeft  size={SIZE} />,
  [RemoteButton.DirectionRight]: <ChevronRight size={SIZE} />,
  [RemoteButton.Select]: <CornerDownLeft size={SIZE} />,
  [RemoteButton.Back]:   <Undo2          size={SIZE} />,
  [RemoteButton.Home]:   <Home           size={SIZE} />,
  [RemoteButton.Menu]:   <Menu           size={SIZE} />,
  [RemoteButton.Exit]:   <X              size={SIZE} />,
  [RemoteButton.Guide]:  <LayoutGrid     size={SIZE} />,
  [RemoteButton.Info]:   <Info           size={SIZE} />,
  // Channel
  [RemoteButton.ChannelUp]:   <ChevronUp   size={SIZE} />,
  [RemoteButton.ChannelDown]: <ChevronDown size={SIZE} />,
  // Transport
  [RemoteButton.Play]:          <Play        size={SIZE} />,
  [RemoteButton.Pause]:         <Pause       size={SIZE} />,
  [RemoteButton.PlayPause]:     <PlayCircle  size={SIZE} />,
  [RemoteButton.Stop]:          <Square      size={SIZE} />,
  [RemoteButton.FastForward]:   <FastForward size={SIZE} />,
  [RemoteButton.Rewind]:        <Rewind      size={SIZE} />,
  [RemoteButton.NextTrack]:     <SkipForward size={SIZE} />,
  [RemoteButton.PreviousTrack]: <SkipBack    size={SIZE} />,
  [RemoteButton.Record]:        <Circle      size={SIZE} style={{ color: '#ef5350' }} />,
  // Brightness / Other
  [RemoteButton.BrightnessUp]:   <Sun    size={SIZE} />,
  [RemoteButton.BrightnessDown]: <SunDim size={SIZE} />,
  // Colored buttons are styled via color prop, icon = filled circle
  [RemoteButton.Red]:    <Disc size={SIZE} />,
  [RemoteButton.Green]:  <Disc size={SIZE} />,
  [RemoteButton.Yellow]: <Disc size={SIZE} />,
  [RemoteButton.Blue]:   <Disc size={SIZE} />,
};

// Numeric fallback (plain text is fine for digits)
export const BUTTON_TEXT_FALLBACK: Partial<Record<RemoteButton, string>> = {
  [RemoteButton.Number0]: '0',
  [RemoteButton.Number1]: '1',
  [RemoteButton.Number2]: '2',
  [RemoteButton.Number3]: '3',
  [RemoteButton.Number4]: '4',
  [RemoteButton.Number5]: '5',
  [RemoteButton.Number6]: '6',
  [RemoteButton.Number7]: '7',
  [RemoteButton.Number8]: '8',
  [RemoteButton.Number9]: '9',
};

interface RemoteIconProps {
  button: RemoteButton;
  size?: number;
}

export default function RemoteIcon({ button, size = SIZE }: RemoteIconProps) {
  const lucide = BUTTON_LUCIDE_ICONS[button];
  if (lucide) {
    // Clone with potentially different size
    return size !== SIZE
      ? React.cloneElement(lucide, { size } as object)
      : lucide;
  }
  const text = BUTTON_TEXT_FALLBACK[button];
  return <span style={{ fontSize: '1rem', lineHeight: 1 }}>{text ?? '?'}</span>;
}
