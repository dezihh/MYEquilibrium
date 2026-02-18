import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ButtonHTMLAttributes,
  type ReactNode,
} from "react";

type SceneStatus = "active" | "inactive" | "starting" | "stopping";
type TabKey = "scenes" | "devices" | "settings";
type SettingsView = "root" | "icons";

type Scene = {
  id: number;
  name: string;
  devices: string[];
  status: SceneStatus;
};

type Device = {
  id: number;
  name: string;
  model?: string;
  category: string;
};

type UserImage = {
  id: number;
  filename: string;
  path: string;
};

type SettingItem = {
  id: string;
  title: string;
  description?: string;
  icon: "image" | "bluetooth" | "code" | "macro" | "invert";
};

type ButtonVariant =
  | "primary"
  | "outline"
  | "ghost"
  | "danger"
  | "text"
  | "icon";
type ButtonTone = "default" | "danger";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  tone?: ButtonTone;
};

type ListRowProps = {
  leading?: ReactNode;
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
  className?: string;
  clickable?: boolean;
  onClick?: () => void;
};

const defaultScenes: Scene[] = [
  {
    id: 1,
    name: "FirstScene",
    devices: ["Nokia1"],
    status: "inactive",
  },
  {
    id: 2,
    name: "Movie Night",
    devices: ["Projector", "AVR", "Blu-ray"],
    status: "inactive",
  },
];

const defaultDevices: Device[] = [
  {
    id: 1,
    name: "LG OLED",
    model: "C2",
    category: "Display",
  },
  {
    id: 2,
    name: "Denon AVR",
    model: "X2700H",
    category: "Amplifier",
  },
  {
    id: 3,
    name: "Chromecast",
    category: "Player",
  },
];

const settingsItems: SettingItem[] = [
  {
    id: "icons",
    title: "Icons",
    icon: "image",
  },
  {
    id: "bluetooth",
    title: "Bluetooth Devices",
    icon: "bluetooth",
  },
  {
    id: "commands",
    title: "Commands",
    icon: "code",
  },
  {
    id: "macros",
    title: "Macros",
    icon: "macro",
  },
];

const STORAGE_KEY = "equilibrium_hub_url";

const cx = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(" ");

const Button = ({
  variant = "primary",
  tone = "default",
  className,
  ...props
}: ButtonProps) => (
  <button
    className={cx(
      "button",
      `button--${variant}`,
      tone === "danger" && "button--tone-danger",
      className
    )}
    {...props}
  />
);

const IconButton = (props: ButtonHTMLAttributes<HTMLButtonElement>) => (
  <Button variant="icon" {...props} />
);

const ListRow = ({
  leading,
  title,
  subtitle,
  actions,
  className,
  clickable,
  onClick,
}: ListRowProps) => (
  <article
    className={cx("list-row", clickable && "list-row--clickable", className)}
    onClick={onClick}
  >
    {leading}
    <div className="list-row__body">
      <div className="list-row__title">{title}</div>
      {subtitle ? <div className="list-row__subtitle">{subtitle}</div> : null}
    </div>
    {actions ? <div className="list-row__actions">{actions}</div> : null}
  </article>
);

const PageHeader = ({
  title,
  onBack,
}: {
  title: string;
  onBack?: () => void;
}) => (
  <header className={cx("page-header", onBack && "page-header--with-back")}>
    {onBack ? (
      <IconButton
        className="page-header__button"
        onClick={onBack}
        aria-label="Back"
      >
        <span aria-hidden="true">&lt;</span>
      </IconButton>
    ) : null}
    <h2>{title}</h2>
  </header>
);

const PageEmpty = ({ children }: { children: ReactNode }) => (
  <div className="page-empty">{children}</div>
);

const iconMap: Record<SettingItem["icon"], ReactNode> = {
  image: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="5" width="16" height="14" rx="2" />
      <circle cx="9" cy="10" r="1.5" />
      <path d="M6 17l4-4 3 3 3-2 2 3" />
    </svg>
  ),
  bluetooth: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4l4 4-4 4 4 4-4 4V4z" />
      <path d="M8 8l8 8" />
      <path d="M8 16l8-8" />
    </svg>
  ),
  code: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 8l-4 4 4 4" />
      <path d="M15 8l4 4-4 4" />
    </svg>
  ),
  macro: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 7h8M8 12h8M8 17h8" />
      <rect x="4" y="5" width="16" height="14" rx="3" />
    </svg>
  ),
  invert: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4v10" />
      <path d="M8 14c0 2.2 1.8 4 4 4s4-1.8 4-4" />
    </svg>
  ),
};

export default function App() {
  const [hubUrl, setHubUrl] = useState(
    () => window.localStorage.getItem(STORAGE_KEY) || ""
  );
  const [connected, setConnected] = useState(Boolean(hubUrl));
  const [activeTab, setActiveTab] = useState<TabKey>("scenes");
  const [scenes, setScenes] = useState<Scene[]>(defaultScenes);
  const [devices, setDevices] = useState<Device[]>(defaultDevices);
  const [invertImages, setInvertImages] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [settingsView, setSettingsView] = useState<SettingsView>("root");
  const [images, setImages] = useState<UserImage[]>([]);
  const [imagesLoading, setImagesLoading] = useState(false);
  const [imagesError, setImagesError] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const [openImageMenuId, setOpenImageMenuId] = useState<number | null>(null);

  const activeScene = useMemo(
    () => scenes.find((scene) => scene.status === "active"),
    [scenes]
  );

  const handleConnect = () => {
    if (!hubUrl.trim()) return;
    window.localStorage.setItem(STORAGE_KEY, hubUrl.trim());
    setConnected(true);
  };

  const toggleScene = (sceneId: number) => {
    setScenes((prev) =>
      prev.map((scene) => {
        if (scene.id !== sceneId) {
          return { ...scene, status: "inactive" };
        }
        const nextStatus = scene.status === "active" ? "inactive" : "active";
        return { ...scene, status: nextStatus };
      })
    );
  };

  const addScene = () => {
    setScenes((prev) => {
      const nextId = prev.length ? Math.max(...prev.map((s) => s.id)) + 1 : 1;
      return [
        ...prev,
        {
          id: nextId,
          name: `New Scene ${nextId}`,
          devices: ["New Device"],
          status: "inactive",
        },
      ];
    });
  };

  const addDevice = () => {
    setDevices((prev) => {
      const nextId = prev.length ? Math.max(...prev.map((d) => d.id)) + 1 : 1;
      return [
        ...prev,
        {
          id: nextId,
          name: `New Device ${nextId}`,
          category: "Other",
        },
      ];
    });
  };

  const fetchImages = async () => {
    setImagesLoading(true);
    setImagesError(null);
    try {
      const response = await fetch("/images/");
      if (!response.ok) {
        throw new Error(`Failed to load images (${response.status})`);
      }
      const data = (await response.json()) as UserImage[];
      setImages(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setImagesError(message);
    } finally {
      setImagesLoading(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("/images/", {
      method: "POST",
      body,
    });
    if (!response.ok) {
      throw new Error(`Upload failed (${response.status})`);
    }
  };

  const handleImageDelete = async (imageId: number) => {
    const response = await fetch(`/images/${imageId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error(`Delete failed (${response.status})`);
    }
  };

  const handleImageRename = async (imageId: number, filename: string) => {
    const response = await fetch(`/images/${imageId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ filename }),
    });
    if (!response.ok) {
      throw new Error(`Rename failed (${response.status})`);
    }
  };

  const renderScenes = () => (
    <section className="page">
      <PageHeader title="Scenes" />

      <div className="page-summary">
        <div>
          <div className="summary__label">Active scene</div>
          <div className="summary__value">
            {activeScene ? activeScene.name : "None"}
          </div>
        </div>
        <Button variant="outline" onClick={addScene}>
          Create scene
        </Button>
      </div>

      <div className="list">
        {scenes.map((scene) => (
          <ListRow
            key={scene.id}
            leading={
              <div className="list-row__avatar">{scene.name.slice(0, 1)}</div>
            }
            title={scene.name}
            subtitle={scene.devices.join(" • ")}
            actions={
              <>
                <Button
                  variant="text"
                  tone={scene.status === "active" ? "danger" : "default"}
                  onClick={() => toggleScene(scene.id)}
                >
                  {scene.status === "active" ? "Stop" : "Start"}
                </Button>
                <IconButton aria-label="More actions">
                  <span>•••</span>
                </IconButton>
              </>
            }
          />
        ))}
      </div>

      <button className="fab" aria-label="Add scene" onClick={addScene}>
        +
      </button>
    </section>
  );

  const renderDevices = () => (
    <section className="page">
      <PageHeader title="Devices" />

      <div className="list">
        {devices.map((device) => (
          <ListRow
            key={device.id}
            leading={
              <div className="list-row__avatar list-row__avatar--muted">
                {device.name.slice(0, 1)}
              </div>
            }
            title={device.name}
            subtitle={`${device.category}${device.model ? ` • ${device.model}` : ""}`}
            actions={
              <IconButton aria-label="More actions">
                <span>•••</span>
              </IconButton>
            }
          />
        ))}
      </div>

      <button className="fab" aria-label="Add device" onClick={addDevice}>
        +
      </button>
    </section>
  );

  const renderSettingsRoot = () => (
    <section className="page">
      <PageHeader title="Settings" />

      <div className="list">
        {settingsItems.map((item) => (
          <ListRow
            key={item.id}
            clickable
            onClick={() => {
              if (item.id === "icons") {
                setSettingsView("icons");
              }
            }}
            leading={<div className="list-row__icon">{iconMap[item.icon]}</div>}
            title={item.title}
            actions={<span className="list-row__chevron">&gt;</span>}
          />
        ))}
        <ListRow
          className="list-row--stacked"
          leading={<div className="list-row__icon">{iconMap.invert}</div>}
          title="Invert Images in Dark Mode"
          subtitle={
            "Inverts all images for scenes and devices while in dark mode (works especially well for simple icons)."
          }
          actions={
            <label className="switch">
              <input
                type="checkbox"
                checked={invertImages}
                onChange={() => setInvertImages((prev) => !prev)}
              />
              <span className="switch__track" />
            </label>
          }
        />
        <ListRow
          leading={<div className="list-row__icon">D</div>}
          title="Dark Mode"
          actions={
            <label className="switch">
              <input
                type="checkbox"
                checked={darkMode}
                onChange={() => setDarkMode((prev) => !prev)}
              />
              <span className="switch__track" />
            </label>
          }
        />
      </div>
    </section>
  );

  const renderIconsPage = () => (
    <section className="page">
      <PageHeader title="Icons" onBack={() => setSettingsView("root")} />

      {imagesLoading ? (
        <PageEmpty>Loading images...</PageEmpty>
      ) : imagesError ? (
        <PageEmpty>{imagesError}</PageEmpty>
      ) : images.length === 0 ? (
        <PageEmpty>No images yet.</PageEmpty>
      ) : (
        <div className="list list--menu">
          {images.map((image) => (
            <ListRow
              key={image.id}
              leading={
                <div className="list-row__icon list-row__icon--image">
                  <img
                    src={`/images/${image.id}`}
                    alt={image.filename}
                    loading="lazy"
                  />
                </div>
              }
              title={image.filename}
              subtitle={image.path}
              actions={
                <div className="menu-anchor">
                  <IconButton
                    aria-label="Image menu"
                    aria-expanded={openImageMenuId === image.id}
                    onClick={() =>
                      setOpenImageMenuId((current) =>
                        current === image.id ? null : image.id
                      )
                    }
                  >
                    <span>•••</span>
                  </IconButton>
                  {openImageMenuId === image.id && (
                    <div className="menu">
                      <button
                        className="menu__item"
                        onClick={async () => {
                          const nextName = window.prompt(
                            "New name",
                            image.filename
                          );
                          if (!nextName) {
                            setOpenImageMenuId(null);
                            return;
                          }
                          try {
                            await handleImageRename(image.id, nextName);
                            setOpenImageMenuId(null);
                            await fetchImages();
                          } catch (error) {
                            const message =
                              error instanceof Error
                                ? error.message
                                : "Rename failed";
                            setImagesError(message);
                          }
                        }}
                      >
                        Rename
                      </button>
                      <button
                        className="menu__item menu__item--danger"
                        onClick={async () => {
                          try {
                            await handleImageDelete(image.id);
                            setOpenImageMenuId(null);
                            await fetchImages();
                          } catch (error) {
                            const message =
                              error instanceof Error
                                ? error.message
                                : "Delete failed";
                            setImagesError(message);
                          }
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              }
            />
          ))}
        </div>
      )}

      <input
        ref={imageInputRef}
        className="file-input"
        type="file"
        accept="image/*"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) return;
          try {
            await handleImageUpload(file);
            await fetchImages();
          } catch (error) {
            const message =
              error instanceof Error ? error.message : "Upload failed";
            setImagesError(message);
          } finally {
            event.target.value = "";
          }
        }}
      />

      <button
        className="fab"
        aria-label="Add icon"
        onClick={() => imageInputRef.current?.click()}
      >
        +
      </button>
    </section>
  );

  const renderSettings = () =>
    settingsView === "icons" ? renderIconsPage() : renderSettingsRoot();

  useEffect(() => {
    if (settingsView === "icons") {
      fetchImages();
    }
  }, [settingsView]);

  return (
    <div className={`app ${darkMode ? "app--dark" : "app--light"}`}>
      <div className="app__glow" aria-hidden="true" />
      <main className="app__frame">
        {!connected ? (
          <section className="connect">
            <div className="connect__badge">Equilibrium Hub</div>
            <h1 className="connect__title">Connect to your hub</h1>
            <p className="connect__subtitle">
              Enter the URL of your hub to continue.
            </p>
            <label className="field">
              <span>Hub URL</span>
              <input
                value={hubUrl}
                onChange={(event) => setHubUrl(event.target.value)}
                placeholder="192.168.0.123:8000"
              />
            </label>
            <Button variant="primary" onClick={handleConnect}>
              Connect
            </Button>
            <div className="connect__hint">
              Make sure your Equilibrium hub is online and reachable from this
              device.
            </div>
          </section>
        ) : activeTab === "scenes" ? (
          renderScenes()
        ) : activeTab === "devices" ? (
          renderDevices()
        ) : (
          renderSettings()
        )}
      </main>

      <nav className="bottom-nav" aria-label="Primary">
        <button
          className={`bottom-nav__item ${
            activeTab === "scenes" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("scenes")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">▣</span>
          Scenes
        </button>
        <button
          className={`bottom-nav__item ${
            activeTab === "devices" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("devices")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">▢</span>
          Devices
        </button>
        <button
          className={`bottom-nav__item ${
            activeTab === "settings" ? "bottom-nav__item--active" : ""
          }`}
          onClick={() => setActiveTab("settings")}
        >
          <span className="bottom-nav__icon" aria-hidden="true">⚙</span>
          Settings
        </button>
      </nav>
    </div>
  );
}
