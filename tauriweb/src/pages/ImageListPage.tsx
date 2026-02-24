import { useRef } from 'react';
import { useApi } from '../hooks/useApi';
import apiClient from '../api/apiClient';

export default function ImageListPage() {
  const { data: images, loading, error, reload } = useApi(() => apiClient.getImages(), []);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await apiClient.uploadImage(file);
      reload();
    } catch (err) {
      alert(`Upload fehlgeschlagen: ${err}`);
    }
    e.target.value = '';
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bild wirklich löschen?')) return;
    try {
      await apiClient.deleteImage(id);
      reload();
    } catch (err) {
      alert(`Fehler: ${err}`);
    }
  };

  if (loading) return <div className="loading-container">Laden...</div>;
  if (error) return <div className="error-container">Fehler: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Bilder</h2>
        <button className="btn btn-primary btn-sm" onClick={() => fileInputRef.current?.click()}>+ Upload</button>
      </div>
      <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleUpload} />

      {images?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🖼️</div>
          <p>Keine Bilder vorhanden</p>
        </div>
      )}

      <div className="images-grid">
        {images?.map(img => (
          <div key={img.id} className="image-card">
            <img src={apiClient.getImageUrl(img.id)} alt={`Bild ${img.id}`} />
            <div className="image-actions">
              <button className="btn btn-danger btn-sm btn-icon" onClick={() => handleDelete(img.id)}>🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
