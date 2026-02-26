import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ScenesPage from './pages/ScenesPage';
import SceneDetailPage from './pages/SceneDetailPage';
import CreateScenePage from './pages/CreateScenePage';
import DevicesPage from './pages/DevicesPage';
import DeviceDetailPage from './pages/DeviceDetailPage';
import CreateDevicePage from './pages/CreateDevicePage';
import SettingsPage from './pages/SettingsPage';
import CommandListPage from './pages/CommandListPage';
import CreateCommandPage from './pages/CreateCommandPage';
import MacroListPage from './pages/MacroListPage';
import CreateMacroPage from './pages/CreateMacroPage';
import BluetoothDevicesPage from './pages/BluetoothDevicesPage';
import ImageListPage from './pages/ImageListPage';
import ConnectPage from './pages/ConnectPage';
import { AppProvider } from './context/AppContext';

function App() {
  useEffect(() => {
    const handlePress = (e: PointerEvent) => {
      const target = (e.target as Element)?.closest(
        'button, .ctrl-btn, .btn, .fab, .bottom-nav-item, .bottom-nav-menu-trigger, .bottom-nav-menu-item, .scene-card, .list-item[role="button"]'
      );
      if (!target) return;
      target.classList.remove('btn-pressed');
      // Force reflow so animation restarts on repeated clicks
      void (target as HTMLElement).offsetWidth;
      target.classList.add('btn-pressed');
      const cleanup = () => target.classList.remove('btn-pressed');
      target.addEventListener('animationend', cleanup, { once: true });
    };
    document.addEventListener('pointerdown', handlePress);
    return () => document.removeEventListener('pointerdown', handlePress);
  }, []);

  return (
    <AppProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <Routes>
          <Route path="/" element={<Navigate to="/scenes" replace />} />
          <Route path="/connect" element={<ConnectPage />} />
          <Route element={<Layout />}>
            <Route path="/scenes" element={<ScenesPage />} />
            <Route path="/scenes/create" element={<CreateScenePage />} />
            <Route path="/scenes/edit/:id" element={<CreateScenePage />} />
            <Route path="/scenes/:id" element={<SceneDetailPage />} />
            <Route path="/devices" element={<DevicesPage />} />
            <Route path="/devices/create" element={<CreateDevicePage />} />
            <Route path="/devices/edit/:id" element={<CreateDevicePage />} />
            <Route path="/devices/:id" element={<DeviceDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/settings/commands" element={<CommandListPage />} />
            <Route path="/settings/commands/create" element={<CreateCommandPage />} />
            <Route path="/settings/macros" element={<MacroListPage />} />
            <Route path="/settings/macros/create" element={<CreateMacroPage />} />
            <Route path="/settings/bluetooth" element={<BluetoothDevicesPage />} />
            <Route path="/settings/images" element={<ImageListPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
