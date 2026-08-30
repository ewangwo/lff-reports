import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/lff-reports/tools/ibkr-radar/',
  build: {
    outDir: '../tools/ibkr-radar',
    emptyOutDir: true,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
