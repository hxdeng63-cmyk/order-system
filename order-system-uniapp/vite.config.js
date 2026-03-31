import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  base: './',
  define: {
    'process.env': {}
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://47.110.86.191',
        changeOrigin: true
      }
    }
  }
})
