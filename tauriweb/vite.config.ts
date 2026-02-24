import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    clearScreen: false,
    base: env.VITE_BASE || '/ui/',
    server: {
      port: 1420,
      strictPort: true,
    },
    envPrefix: ['VITE_', 'TAURI_'],
    build: {
      outDir: '../web',
      emptyOutDir: true,
      target: process.env.TAURI_PLATFORM === 'windows' ? 'chrome105' : 'safari13',
      minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
      sourcemap: !!process.env.TAURI_DEBUG,
    },
  };
});
