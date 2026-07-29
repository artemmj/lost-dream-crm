<template>
    <div class="app">
        <!-- ===== Не авторизован → показываем AuthPage ===== -->
        <AuthPage v-if="!authStore.isAuthenticated" />

        <!-- ===== Авторизован → основной интерфейс ===== -->
        <template v-else>
            <header class="app__header">
                <h1>CRM System</h1>

                <nav class="app__nav">
                    <button
                        :class="{ active: currentView === 'users' }"
                        @click="currentView = 'users'"
                    >
                        Users
                    </button>
                    <button
                        :class="{ active: currentView === 'customers' }"
                        @click="currentView = 'customers'"
                    >
                        Customers
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
                <UserList v-if="currentView === 'users'" />
                <CustomerList v-else-if="currentView === 'customers'" />
            </main>
        </template>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import AuthPage from './components/AuthPage.vue'
import UserList from './components/UserList.vue'
import CustomerList from './components/CustomerList.vue'

const authStore = useAuthStore()
const currentView = ref('users')

// При загрузке: если токен в localStorage есть — подтягиваем профиль
onMounted(() => {
    authStore.init()
})

async function handleLogout() {
    await authStore.logout()
    // После clearLocal() isAuthenticated станет false →
    // Vue автоматически покажет AuthPage
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f9fafb;
    color: #1f2937;
}

.app { min-height: 100vh; }

.app__header {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 16px 32px;
    background: white;
    border-bottom: 1px solid #e5e7eb;
}

.app__header h1 { font-size: 20px; color: #4f46e5; }

.app__nav { display: flex; gap: 8px; }

.app__nav button {
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.app__nav button:hover { background: #f3f4f6; }

.app__nav button.active {
    background: #4f46e5;
    color: white;
    border-color: #4f46e5;
}

.app__auth { margin-left: auto; }

.app__auth-placeholder { font-size: 13px; color: #9ca3af; }

.app__main { padding: 32px; }

.app__auth {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.app__auth-user {
    font-size: 0.9rem;
    color: #333;
}

.app__logout {
    padding: 0.35rem 0.75rem;
    background: #d32f2f;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
}

.app__logout:hover {
    background: #b71c1c;
}
</style>