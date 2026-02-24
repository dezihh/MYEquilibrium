import { useNavigate, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/scenes', label: 'Szenen', icon: '🎬' },
  { path: '/devices', label: 'Geräte', icon: '📺' },
  { path: '/settings', label: 'Einstellungen', icon: '⚙️' },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => (
        <button
          key={item.path}
          className={`bottom-nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}
          onClick={() => navigate(item.path)}
        >
          <span className="nav-icon">{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  );
}
