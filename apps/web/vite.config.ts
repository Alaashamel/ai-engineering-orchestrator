import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/workflows': 'http://localhost:8000',
      '/projects': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/eval': 'http://localhost:8000',
    },
  },
})
