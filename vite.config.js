import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: path.resolve('static/landing-build'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve('frontend/landing-entry.jsx'),
      output: {
        entryFileNames: 'landing-galaxy.js',
        assetFileNames: 'landing-galaxy.[ext]'
      }
    }
  }
});
