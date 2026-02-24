import { useEffect, useRef } from 'react';

export function useWebSocket<T>(
  factory: (onMessage: (data: T) => void, onError: (e: Event) => void) => WebSocket,
  onMessage: (data: T) => void,
  enabled = true
) {
  const wsRef = useRef<WebSocket | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!enabled) return;
    const ws = factory(
      (data) => onMessageRef.current(data),
      (e) => console.error('WebSocket error', e)
    );
    wsRef.current = ws;
    return () => { ws.close(); };
  }, [factory, enabled]);

  return wsRef;
}
