import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: false
      },
      manifest: {
        name: 'Control de Asistencia',
        short_name: 'Asistencia',
        description: 'Sistema de Control de Asistencia Facial - Municipalidad Provincial de Cajamarca',
        theme_color: '#1a3a6b',
        background_color: '#1a3a6b',
        display: 'standalone',
        icons: [
          { src: '/logo.png', sizes: '192x192', type: 'image/png' },
          { src: '/logo.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    /*host:true,*/
    port: 5173
    
    /* para mis pruebas con ngrok necesito esto dentro de server
    allowedHosts: true
    */
  }
})