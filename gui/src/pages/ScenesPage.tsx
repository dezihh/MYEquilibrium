import { Button, IconButton } from "../components/Button";
import { ListRow } from "../components/ListRow";
import { PageHeader } from "../components/Page";
import type { Scene } from "../types";

export type ScenesPageProps = {
  scenes: Scene[];
  activeScene?: Scene;
  onAddScene: () => void;
  onToggleScene: (sceneId: number) => void;
};

export const ScenesPage = ({
  scenes,
  activeScene,
  onAddScene,
  onToggleScene,
}: ScenesPageProps) => (
  <section className="page">
    <PageHeader title="Scenes" />

    <div className="page-summary">
      <div>
        <div className="summary__label">Active scene</div>
        <div className="summary__value">
          {activeScene ? activeScene.name : "None"}
        </div>
      </div>
      <Button variant="outline" onClick={onAddScene}>
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
                onClick={() => onToggleScene(scene.id)}
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

    <button className="fab" aria-label="Add scene" onClick={onAddScene}>
      +
    </button>
  </section>
);
