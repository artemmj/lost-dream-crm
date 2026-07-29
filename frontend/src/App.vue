<template>
    <div class="app">
        <!-- ===== Не авторизован → показываем AuthPage ===== -->
        <AuthPage v-if="!authStore.isAuthenticated" />

        <!-- ===== Авторизован → основной интерфейс с Роутером ===== -->
        <template v-else>
            <header class="app__header">
                <h1 
                    class="app__logo" 
                    @click="router.push('/')"
                    style="cursor: pointer;"
                >
                    CRM System
                </h1>

                <nav class="app__nav">
                    <!-- Используем router.push для смены URL -->
                    <button
                        :class="{ active: route.path === '/' }"
                        @click="router.push('/')"
                    >
                        Главная
                    </button>
                    <button
                        :class="{ active: route.path.startsWith('/users') }"
                        @click="router.push('/users')"
                    >
                        Пользователи
                    </button>
                    <button
                        :class="{ active: route.path.startsWith('/customers') }"
                        @click="router.push('/customers')"
                    >
                        Клиенты
                    </button>
                </nav>

                <div class="app__auth">
                    <span class="app__auth-user">
                        👤 {{ authStore.currentUser?.first_name }}
                        {{ authStore.currentUser?.last_name }}
                    </span>
                    <button
                        class="app__logout"
                        :disabled="authStore.loading"
                        @click="handleLogout"
                    >
                        Logout
                    </button>
                </div>
            </header>

            <main class="app__main">
                <!-- Сюда Роутер будет подставлять компоненты: Dashboard, UserList и т.д. -->
                <RouterView />
            </main>
        </template>
    </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' // <--- Импортируем хуки роутера
import { useAuthStore } from './stores/auth'
import AuthPage from './components/AuthPage.vue'

const authStore = useAuthStore()
const route = useRoute()   // Текущий маршрут
const router = useRouter() // Экземпляр роутера для навигации

onMounted(() => {
    authStore.init()
})

async function handleLogout() {
    await authStore.logout()
    // После выхода принудительно кидаем на главную (которая покажет AuthPage)
    router.push('/')
}
</script>

<style>
/* Твои стили остаются без изменений */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f9fafb;
    color: #1f2937;
}
.app { min-height: 100vh; display: flex; flex-direction: column; }
.app__header {
    display: flex; align-items: center; gap: 24px; padding: 16px 32px;
    background: white; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; z-index: 10;
}
.app__logo { font-size: 20px; color: #4f46e5; user-select: none; }
.app__nav { display: flex; gap: 8px; }
.app__nav button {
    padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 6px;
    background: white; cursor: pointer; font-size: 14px; transition: all 0.2s;
}
.app__nav button:hover { background: #f3f4f6; }
.app__nav button.active { background: #4f46e5; color: white; border-color: #4f46e5; }
.app__auth { margin-left: auto; display: flex; align-items: center; gap: 0.75rem; }
.app__auth-user { font-size: 0.9rem; color: #333; font-weight: 500; }
.app__logout {
    padding: 0.35rem 0.75rem; background: #d32f2f; color: #fff; border: none;
    border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: background 0.2s;
}
.app__logout:hover:not(:disabled) { background: #b71c1c; }
.app__logout:disabled { opacity: 0.6; cursor: not-allowed; }
.app__main { padding: 32px; flex: 1; }
</style>
