export type SwitchProps = {
  checked: boolean;
  onChange: () => void;
  ariaLabel?: string;
};

export const Switch = ({ checked, onChange, ariaLabel }: SwitchProps) => (
  <label className="switch">
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      aria-label={ariaLabel}
    />
    <span className="switch__track" />
  </label>
);
