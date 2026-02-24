import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import BottomNav from './BottomNav';

const pageTitles: Record<string, string> = {
  '/scenes': 'Szenen',
  '/devices': 'Geräte',
  '/settings': 'Einstellungen',
  '/settings/commands': 'Befehle',
  '/settings/macros': 'Makros',
  '/settings/bluetooth': 'Bluetooth',
  '/settings/images': 'Bilder',
};

function getTitle(pathname: string): string {
  if (pageTitles[pathname]) return pageTitles[pathname];
  if (pathname.includes('/create')) return 'Erstellen';
  if (pathname.includes('/edit/')) return 'Bearbeiten';
  if (pathname.includes('/scenes/')) return 'Szene Details';
  if (pathname.includes('/devices/')) return 'Gerät Details';
  return 'Equilibrium';
}

function showBackButton(pathname: string): boolean {
  return pathname !== '/scenes' && pathname !== '/devices' && pathname !== '/settings';
}

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const title = getTitle(location.pathname);

  return (
    <div className="app-layout">
      <header className="app-bar">
        {showBackButton(location.pathname) && (
          <button className="back-btn" onClick={() => navigate(-1)}>←</button>
        )}
        <h1>{title}</h1>
      </header>
      <main className="content-area">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
