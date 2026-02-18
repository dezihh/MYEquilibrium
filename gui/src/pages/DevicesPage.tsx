import { IconButton } from "../components/Button";
import { ListRow } from "../components/ListRow";
import { PageHeader } from "../components/Page";
import type { Device } from "../types";

export type DevicesPageProps = {
  devices: Device[];
  onAddDevice: () => void;
};

export const DevicesPage = ({ devices, onAddDevice }: DevicesPageProps) => (
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

    <button className="fab" aria-label="Add device" onClick={onAddDevice}>
      +
    </button>
  </section>
);
