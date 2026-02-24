import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AppContextType {
  hubUrl: string;
  setHubUrl: (url: string) => void;
  isConnected: boolean;
  currentScene: number | null;
  setCurrentScene: (id: number | null) => void;
  isTauri: boolean;
}

const AppContext = createContext<AppContextType>({
  hubUrl: '',
  setHubUrl: () => {},
  isConnected: false,
  currentScene: null,
  setCurrentScene: () => {},
  isTauri: false,
});

function detectTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

export function AppProvider({ children }: { children: ReactNode }) {
  const isTauri = detectTauri();
  const [hubUrl, setHubUrlState] = useState<string>(() => {
    if (isTauri) return localStorage.getItem('hubUrl') || '';
    return window.location.origin;
  });
  const [isConnected, setIsConnected] = useState(false);
  const [currentScene, setCurrentScene] = useState<number | null>(null);

  const setHubUrl = (url: string) => {
    setHubUrlState(url);
    if (isTauri) localStorage.setItem('hubUrl', url);
  };

  useEffect(() => {
    if (!hubUrl) return;
    fetch(`${hubUrl}/info`)
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false));
  }, [hubUrl]);

  return (
    <AppContext.Provider value={{ hubUrl, setHubUrl, isConnected, currentScene, setCurrentScene, isTauri }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  return useContext(AppContext);
}
