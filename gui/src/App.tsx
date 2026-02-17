import { useMemo, useState } from "react";

type SceneStatus = "active" | "inactive" | "starting" | "stopping";

type Scene = {
  id: number;
  name: string;
  devices: string[];
  status: SceneStatus;
};

const defaultScenes: Scene[] = [
  {
    id: 1,
    name: "Living Room",
    devices: ["LG TV", "Denon AVR", "Chromecast"],
    status: "active",
  },
  {
    id: 2,
    name: "Movie Night",
    devices: ["Projector", "AV Receiver", "Blu-ray"],
    status: "inactive",
  },
  {
    id: 3,
    name: "Bedroom",
    devices: ["Samsung TV", "Soundbar"],
    status: "inactive",
  },
];

const STORAGE_KEY = "equilibrium_hub_url";

export default function App() {
  const [hubUrl, setHubUrl] = useState(
    () => window.localStorage.getItem(STORAGE_KEY) || ""
  );
  const [connected, setConnected] = useState(Boolean(hubUrl));
  const [scenes, setScenes] = useState<Scene[]>(defaultScenes);

  const activeScene = useMemo(
    () => scenes.find((scene) => scene.status === "active"),
    [scenes]
  );

  const handleConnect = () => {
    if (!hubUrl.trim()) return;
    window.localStorage.setItem(STORAGE_KEY, hubUrl.trim());
    setConnected(true);
  };

  const handleDisconnect = () => {
    setConnected(false);
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

  return (
    <div className="app">
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
            <button className="primary-button" onClick={handleConnect}>
              Connect
            </button>
            <div className="connect__hint">
              Make sure your Equilibrium hub is online and reachable from this
              device.
            </div>
          </section>
        ) : (
          <section className="scenes">
            <header className="scenes__header">
              <div>
                <h2>Scenes</h2>
                <p>Quick control for your active setups.</p>
              </div>
              <div className="scenes__actions">
                <div className="status-pill">
                  <span className="status-pill__dot" />
                  {hubUrl}
                </div>
                <button className="ghost-button" onClick={handleDisconnect}>
                  Disconnect
                </button>
              </div>
            </header>

            <div className="scenes__summary">
              <div>
                <div className="summary__label">Active scene</div>
                <div className="summary__value">
                  {activeScene ? activeScene.name : "None"}
                </div>
              </div>
              <button className="outline-button">Create scene</button>
            </div>

            <div className="scene-list">
              {scenes.map((scene) => (
                <article className="scene-card" key={scene.id}>
                  <div className="scene-card__icon">
                    {scene.name.slice(0, 1)}
                  </div>
                  <div className="scene-card__body">
                    <div className="scene-card__title">{scene.name}</div>
                    <div className="scene-card__subtitle">
                      {scene.devices.join(" • ")}
                    </div>
                    <div className={`scene-card__status scene-card__status--${scene.status}`}>
                      {scene.status}
                    </div>
                  </div>
                  <div className="scene-card__actions">
                    <button
                      className={
                        scene.status === "active"
                          ? "danger-button"
                          : "primary-button"
                      }
                      onClick={() => toggleScene(scene.id)}
                    >
                      {scene.status === "active" ? "Stop" : "Start"}
                    </button>
                    <button className="icon-button" aria-label="More actions">
                      <span>•••</span>
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <button className="fab" aria-label="Add scene">
              +
            </button>
          </section>
        )}
      </main>

      <nav className="bottom-nav" aria-label="Primary">
        <button className="bottom-nav__item bottom-nav__item--active">
          <span className="bottom-nav__icon">◼</span>
          Scenes
        </button>
        <button className="bottom-nav__item" disabled>
          <span className="bottom-nav__icon">◆</span>
          Devices
        </button>
        <button className="bottom-nav__item" disabled>
          <span className="bottom-nav__icon">●</span>
          Settings
        </button>
      </nav>
    </div>
  );
}
