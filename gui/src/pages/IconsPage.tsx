import type { ChangeEvent, RefObject } from "react";
import { IconButton } from "../components/Button";
import { ListRow } from "../components/ListRow";
import { Menu, MenuAnchor, MenuItem } from "../components/Menu";
import { PageEmpty, PageHeader } from "../components/Page";
import type { UserImage } from "../types";

export type IconsPageProps = {
  images: UserImage[];
  loading: boolean;
  error: string | null;
  openMenuId: number | null;
  onToggleMenu: (imageId: number) => void;
  onCloseMenu: () => void;
  onRename: (imageId: number, filename: string) => Promise<void>;
  onDelete: (imageId: number) => Promise<void>;
  onUpload: (file: File) => Promise<void>;
  onBack: () => void;
  imageInputRef: RefObject<HTMLInputElement>;
};

export const IconsPage = ({
  images,
  loading,
  error,
  openMenuId,
  onToggleMenu,
  onCloseMenu,
  onRename,
  onDelete,
  onUpload,
  onBack,
  imageInputRef,
}: IconsPageProps) => {
  const handleRename = async (image: UserImage) => {
    const nextName = window.prompt("New name", image.filename);
    if (!nextName) {
      onCloseMenu();
      return;
    }
    await onRename(image.id, nextName);
    onCloseMenu();
  };

  const handleDelete = async (imageId: number) => {
    await onDelete(imageId);
    onCloseMenu();
  };

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await onUpload(file);
    event.target.value = "";
  };

  return (
    <section className="page">
      <PageHeader title="Icons" onBack={onBack} />

      {loading ? (
        <PageEmpty>Loading images...</PageEmpty>
      ) : error ? (
        <PageEmpty>{error}</PageEmpty>
      ) : images.length === 0 ? (
        <PageEmpty>No images yet.</PageEmpty>
      ) : (
        <div className="list list--menu">
          {images.map((image) => (
            <ListRow
              key={image.id}
              leading={
                <div className="list-row__icon list-row__icon--image">
                  <img
                    src={`/images/${image.id}`}
                    alt={image.filename}
                    loading="lazy"
                  />
                </div>
              }
              title={image.filename}
              subtitle={image.path}
              actions={
                <MenuAnchor>
                  <IconButton
                    aria-label="Image menu"
                    aria-expanded={openMenuId === image.id}
                    onClick={() => onToggleMenu(image.id)}
                  >
                    <span>•••</span>
                  </IconButton>
                  {openMenuId === image.id && (
                    <Menu>
                      <MenuItem onClick={() => handleRename(image)}>
                        Rename
                      </MenuItem>
                      <MenuItem tone="danger" onClick={() => handleDelete(image.id)}>
                        Delete
                      </MenuItem>
                    </Menu>
                  )}
                </MenuAnchor>
              }
            />
          ))}
        </div>
      )}

      <input
        ref={imageInputRef}
        className="file-input"
        type="file"
        accept="image/*"
        onChange={handleUpload}
      />

      <button
        className="fab"
        aria-label="Add icon"
        onClick={() => imageInputRef.current?.click()}
      >
        +
      </button>
    </section>
  );
};
