import { useState } from "react";

export const useMenuState = <T,>() => {
  const [openId, setOpenId] = useState<T | null>(null);

  const isOpen = (id: T) => openId === id;
  const toggle = (id: T) => {
    setOpenId((current) => (current === id ? null : id));
  };
  const close = () => setOpenId(null);

  return { openId, isOpen, toggle, close };
};
