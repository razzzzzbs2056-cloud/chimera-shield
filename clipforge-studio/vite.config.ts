import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward optional AI calls to the FastAPI backend during development so the
    // browser app can stay on a relative /api path. Override the target with the
    // VITE_AI_API_BASE env var in production builds.
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
