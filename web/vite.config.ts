import { defineConfig } from 'vite';
export default defineConfig({
  root: 'public',
  publicDir: '.',
  server: { 
    port: 5173,
    host: '0.0.0.0'
  },
  build: {
    outDir: '../dist'
  },
  resolve: {
    alias: {
      '/src': '/app/src'
    }
  }
});
