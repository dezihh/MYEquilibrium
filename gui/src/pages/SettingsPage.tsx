import { ListRow } from "../components/ListRow";
import { PageHeader } from "../components/Page";
import { Switch } from "../components/Switch";
import { settingIcons } from "../components/icons";
import type { SettingItem } from "../types";

export type SettingsPageProps = {
  items: SettingItem[];
  invertImages: boolean;
  darkMode: boolean;
  onToggleInvert: () => void;
  onToggleDarkMode: () => void;
  onSelectItem?: (id: string) => void;
};

export const SettingsPage = ({
  items,
  invertImages,
  darkMode,
  onToggleInvert,
  onToggleDarkMode,
  onSelectItem,
}: SettingsPageProps) => (
  <section className="page">
    <PageHeader title="Settings" />

    <div className="list">
      {items.map((item) => (
        <ListRow
          key={item.id}
          clickable={Boolean(onSelectItem)}
          onClick={() => onSelectItem?.(item.id)}
          leading={<div className="list-row__icon">{settingIcons[item.icon]}</div>}
          title={item.title}
          actions={<span className="list-row__chevron">&gt;</span>}
        />
      ))}
      <ListRow
        className="list-row--stacked"
        leading={<div className="list-row__icon">{settingIcons.invert}</div>}
        title="Invert Images in Dark Mode"
        subtitle={
          "Inverts all images for scenes and devices while in dark mode (works especially well for simple icons)."
        }
        actions={
          <Switch
            checked={invertImages}
            onChange={onToggleInvert}
            ariaLabel="Invert images"
          />
        }
      />
      <ListRow
        leading={<div className="list-row__icon">D</div>}
        title="Dark Mode"
        actions={
          <Switch
            checked={darkMode}
            onChange={onToggleDarkMode}
            ariaLabel="Dark mode"
          />
        }
      />
    </div>
  </section>
);
