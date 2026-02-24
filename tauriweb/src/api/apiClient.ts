import { Device, DeviceCreate } from '../models/device';
import { Scene, SceneCreate } from '../models/scene';
import { Command, CommandCreate } from '../models/command';
import { Macro, MacroCreate } from '../models/macro';
import { UserImage } from '../models/image';
import { BleDevice } from '../models/bleDevice';
import { StatusReport } from '../models/statusReport';

function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

function getBaseUrl(): string {
  if (isTauri()) {
    return localStorage.getItem('hubUrl') || 'http://localhost:8000';
  }
  return import.meta.env.VITE_API_BASE || window.location.origin;
}

class ApiClient {
  private get baseUrl(): string {
    return getBaseUrl();
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }
    if (response.status === 204) return undefined as T;
    return response.json();
  }

  // Devices
  async getDevices(): Promise<Device[]> {
    return this.request<Device[]>('/devices/');
  }
  async createDevice(data: DeviceCreate): Promise<Device> {
    return this.request<Device>('/devices/', { method: 'POST', body: JSON.stringify(data) });
  }
  async getDevice(id: number): Promise<Device> {
    return this.request<Device>(`/devices/${id}`);
  }
  async updateDevice(id: number, data: Partial<DeviceCreate>): Promise<Device> {
    return this.request<Device>(`/devices/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  }
  async deleteDevice(id: number): Promise<void> {
    return this.request<void>(`/devices/${id}`, { method: 'DELETE' });
  }

  // Scenes
  async getScenes(): Promise<Scene[]> {
    return this.request<Scene[]>('/scenes/');
  }
  async createScene(data: SceneCreate): Promise<Scene> {
    return this.request<Scene>('/scenes/', { method: 'POST', body: JSON.stringify(data) });
  }
  async updateScene(id: number, data: Partial<SceneCreate>): Promise<Scene> {
    return this.request<Scene>(`/scenes/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  }
  async deleteScene(id: number): Promise<void> {
    return this.request<void>(`/scenes/${id}`, { method: 'DELETE' });
  }
  async startScene(id: number): Promise<void> {
    return this.request<void>(`/scenes/${id}/start`, { method: 'POST' });
  }
  async stopScenes(): Promise<void> {
    return this.request<void>('/scenes/stop', { method: 'POST' });
  }

  // Commands
  async getCommands(): Promise<Command[]> {
    return this.request<Command[]>('/commands/');
  }
  async createCommand(data: CommandCreate): Promise<Command> {
    return this.request<Command>('/commands/', { method: 'POST', body: JSON.stringify(data) });
  }
  async getCommand(id: number): Promise<Command> {
    return this.request<Command>(`/commands/${id}`);
  }
  async deleteCommand(id: number): Promise<void> {
    return this.request<void>(`/commands/${id}`, { method: 'DELETE' });
  }
  async sendCommand(id: number): Promise<void> {
    return this.request<void>(`/commands/${id}/send`, { method: 'POST' });
  }

  // Macros
  async getMacros(): Promise<Macro[]> {
    return this.request<Macro[]>('/macros/');
  }
  async createMacro(data: MacroCreate): Promise<Macro> {
    return this.request<Macro>('/macros/', { method: 'POST', body: JSON.stringify(data) });
  }
  async updateMacro(id: number, data: Partial<MacroCreate>): Promise<Macro> {
    return this.request<Macro>(`/macros/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  }
  async deleteMacro(id: number): Promise<void> {
    return this.request<void>(`/macros/${id}`, { method: 'DELETE' });
  }
  async executeMacro(id: number): Promise<void> {
    return this.request<void>(`/macros/${id}/execute`, { method: 'POST' });
  }

  // Images
  async getImages(): Promise<UserImage[]> {
    return this.request<UserImage[]>('/images/');
  }
  async uploadImage(file: File): Promise<UserImage> {
    const form = new FormData();
    form.append('file', file);
    const url = `${this.baseUrl}/images/`;
    const response = await fetch(url, { method: 'POST', body: form });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
  async deleteImage(id: number): Promise<void> {
    return this.request<void>(`/images/${id}`, { method: 'DELETE' });
  }
  getImageUrl(id: number): string {
    return `${this.baseUrl}/images/${id}`;
  }

  // Bluetooth
  async getBleDevices(): Promise<BleDevice[]> {
    return this.request<BleDevice[]>('/bluetooth/devices');
  }
  async startAdvertisement(): Promise<void> {
    return this.request<void>('/bluetooth/start_advertisement', { method: 'POST' });
  }
  async startPairing(): Promise<void> {
    return this.request<void>('/bluetooth/start_pairing', { method: 'POST' });
  }
  async connectBle(mac: string): Promise<void> {
    return this.request<void>(`/bluetooth/connect/${mac}`, { method: 'POST' });
  }
  async disconnectBle(): Promise<void> {
    return this.request<void>('/bluetooth/disconnect', { method: 'POST' });
  }
  async removeBleDevice(mac: string): Promise<void> {
    return this.request<void>(`/bluetooth/remove/${mac}`, { method: 'DELETE' });
  }

  // System
  async getStatus(): Promise<StatusReport> {
    return this.request<StatusReport>('/system/status');
  }
  async getInfo(): Promise<unknown> {
    return this.request<unknown>('/info');
  }

  // WebSockets
  createStatusWebSocket(onMessage: (data: StatusReport) => void, onError?: (e: Event) => void): WebSocket {
    const wsUrl = this.baseUrl.replace(/^http/, 'ws') + '/ws/status';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => { try { onMessage(JSON.parse(e.data)); } catch { /* ignore parse errors */ } };
    if (onError) ws.onerror = onError;
    return ws;
  }
  createPairingWebSocket(onMessage: (data: unknown) => void, onError?: (e: Event) => void): WebSocket {
    const wsUrl = this.baseUrl.replace(/^http/, 'ws') + '/ws/bt_pairing';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => { try { onMessage(JSON.parse(e.data)); } catch { /* ignore parse errors */ } };
    if (onError) ws.onerror = onError;
    return ws;
  }
  createCommandsWebSocket(onMessage: (data: unknown) => void, onError?: (e: Event) => void): WebSocket {
    const wsUrl = this.baseUrl.replace(/^http/, 'ws') + '/ws/commands';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => { try { onMessage(JSON.parse(e.data)); } catch { /* ignore parse errors */ } };
    if (onError) ws.onerror = onError;
    return ws;
  }
}

export { ApiClient };
export default new ApiClient();
