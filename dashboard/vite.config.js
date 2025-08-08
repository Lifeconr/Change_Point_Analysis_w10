// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  // Configure esbuild to correctly parse JSX in .js and .jsx files
  esbuild: {
    loader: 'jsx', // Default loader for files processed by esbuild
    include: /src\/.*\.(js|jsx)$/, // Include all .js and .jsx files within src/
    exclude: [], // No specific files to exclude
  },
  // Ensure dependency optimization also handles JSX in .js and .jsx files
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
        '.jsx': 'jsx', // Explicitly tell esbuild to treat .jsx as JSX here
      },
    },
  },
})
