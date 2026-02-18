import type { ReactNode } from "react";
import { cx } from "../utils/cx";
import { IconButton } from "./Button";

export const PageHeader = ({
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

export const PageEmpty = ({ children }: { children: ReactNode }) => (
  <div className="page-empty">{children}</div>
);
