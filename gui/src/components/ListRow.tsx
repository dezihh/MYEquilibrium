import type { ReactNode } from "react";
import { cx } from "../utils/cx";

export type ListRowProps = {
  leading?: ReactNode;
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
  className?: string;
  clickable?: boolean;
  onClick?: () => void;
};

export const ListRow = ({
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
