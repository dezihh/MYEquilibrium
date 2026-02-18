import { Button } from "../components/Button";

export type ConnectPageProps = {
  hubUrl: string;
  onHubUrlChange: (value: string) => void;
  onConnect: () => void;
};

export const ConnectPage = ({
  hubUrl,
  onHubUrlChange,
  onConnect,
}: ConnectPageProps) => (
  <section className="connect">
    <div className="connect__badge">Equilibrium Hub</div>
    <h1 className="connect__title">Connect to your hub</h1>
    <p className="connect__subtitle">Enter the URL of your hub to continue.</p>
    <label className="field">
      <span>Hub URL</span>
      <input
        value={hubUrl}
        onChange={(event) => onHubUrlChange(event.target.value)}
        placeholder="192.168.0.123:8000"
      />
    </label>
    <Button variant="primary" onClick={onConnect}>
      Connect
    </Button>
    <div className="connect__hint">
      Make sure your Equilibrium hub is online and reachable from this device.
    </div>
  </section>
);
