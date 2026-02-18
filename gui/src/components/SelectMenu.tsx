import { useMemo, useState, type ReactNode } from "react";
import { cx } from "../utils/cx";

export type SelectOption = {
  value: string;
  label: string;
  icon?: ReactNode;
};

export type SelectMenuProps = {
  id?: string;
  label?: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
};

export const SelectMenu = ({
  id,
  label,
  value,
  options,
  onChange,
  placeholder = "Select",
  disabled,
}: SelectMenuProps) => {
  const [open, setOpen] = useState(false);
  const selected = useMemo(
    () => options.find((option) => option.value === value),
    [options, value]
  );

  return (
    <div className="select-menu">
      {label ? (
        <label className="form-label" htmlFor={id}>
          {label}
        </label>
      ) : null}
      <button
        id={id}
        type="button"
        className={cx("form-control", "form-control--menu")}
        onClick={() => setOpen((current) => !current)}
        disabled={disabled}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span className="select-menu__content">
          {selected?.icon ? (
            <span className="select-menu__icon">{selected.icon}</span>
          ) : null}
          <span className="select-menu__label">
            {selected?.label ?? placeholder}
          </span>
        </span>
        <span className="select-menu__chevron" aria-hidden="true">
          v
        </span>
      </button>
      {open ? (
        <div className="select-menu__list" role="listbox">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              className={cx(
                "select-menu__item",
                option.value === value && "select-menu__item--active"
              )}
              onClick={() => {
                onChange(option.value);
                setOpen(false);
              }}
              role="option"
              aria-selected={option.value === value}
            >
              {option.icon ? (
                <span className="select-menu__icon">{option.icon}</span>
              ) : null}
              <span className="select-menu__label">{option.label}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
};
