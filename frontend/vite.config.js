import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        port: 3000,
        host: true, // Слушает все интерфейсы (0.0.0.0)
        strictPort: false,
        proxy: {
            // Все запросы к /api перенаправляем на наш Nginx Gateway
            '/api': {
                target: 'http://nginx:80', // 'nginx' - это имя сервиса в docker-compose
                changeOrigin: true,
                secure: false,
            },
        },
    },
})
