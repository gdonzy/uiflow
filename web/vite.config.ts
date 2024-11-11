import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Compoents from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    }
  },
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'vuex', 'vue-i18n'],
      resolvers: [ElementPlusResolver()],
    }),
    Compoents({
      resolvers: [ElementPlusResolver()],
    })
  ],
  server: {
    port: 5050,
    open: true,
    proxy: {
      '/flows': {
        target: 'http://localhost:8009',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/a/, '')
      },
      '/exec': {
        target: 'http://localhost:8009',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/a/, '')
      },
      '/ws/flow': {
        target: 'ws://localhost:8009/ws/flow',
        ws: true,
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: "modern-compiler",
      }
    }
  }
})
