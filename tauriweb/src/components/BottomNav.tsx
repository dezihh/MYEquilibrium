import { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/scenes', label: 'Szenen', icon: '🎬' },
  { path: '/devices', label: 'Geräte', icon: '📺' },
  { path: '/settings', label: 'Einstellungen', icon: '⚙️' },
];

// internal: React Router navigate, external: open in new tab
const quickLinks: { label: string; internal?: string; external?: string }[] = [
  { label: 'RemoteAdmin',    internal: '/scenes' },
  { label: 'RemoteControl',  internal: '/scenes' },
  { label: 'Flutter',        external: '/gui/' },
  { label: 'REST-Interface', external: '/docs' },
  { label: 'ReDoc',          external: '/redoc' },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (!menuRef.current?.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    if (menuOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [menuOpen]);

  function handleQuickLink(item: typeof quickLinks[0]) {
    setMenuOpen(false);
    if (item.internal) {
      navigate(item.internal);
    } else if (item.external) {
      window.open(item.external, '_blank');
    }
  }

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
      <div className="bottom-nav-menu" ref={menuRef}>
        <button
          className={`bottom-nav-menu-trigger ${menuOpen ? 'active' : ''}`}
          aria-label="Menü öffnen"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((prev) => !prev)}
        >
          <svg className="dots-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="10" cy="4" r="2.2" />
            <circle cx="10" cy="10" r="2.2" />
            <circle cx="10" cy="16" r="2.2" />
          </svg>
          <span className="dots-label">Mehr</span>
        </button>
        {menuOpen && (
          <div className="bottom-nav-menu-panel" role="menu" aria-label="Schnellzugriff">
            {quickLinks.map((item) => (
              <button
                key={item.label}
                className="bottom-nav-menu-item"
                role="menuitem"
                onClick={() => handleQuickLink(item)}
              >
                {item.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
