import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // During development, forward API calls to the FastAPI server.
    proxy: { '/drives': 'http://127.0.0.1:8000', '/auth': 'http://127.0.0.1:8000' },
  },
})
