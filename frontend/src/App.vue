<template>
    <div class="app">
        <header class="app__header">
            <h1>CRM System</h1>
            <nav class="app__nav">
                <button 
                    :class="{ active: currentView === 'users' }"
                    @click="currentView = 'users'"
                >
                    Users (CRM)
                </button>
                <button 
                    :class="{ active: currentView === 'customers' }"
                    @click="currentView = 'customers'"
                >
                    Customers
                </button>
                <!-- ЗАГОТОВКА: Добавление новых сервисов -->
                <!-- <button 
                    :class="{ active: currentView === 'products' }"
                    @click="currentView = 'products'"
                >
                    Products
                </button> -->
            </nav>
            <div class="app__auth">
                <span class="app__auth-placeholder">🔓 No auth (JWT placeholder)</span>
            </div>
        </header>

        <main class="app__main">
            <UserList v-if="currentView === 'users'" />
            <CustomerList v-else-if="currentView === 'customers'" />
            <!-- ЗАГОТОВКА: Другие view -->
            <!-- <ProductList v-else-if="currentView === 'products'" /> -->
        </main>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import UserList from './components/UserList.vue'
import CustomerList from './components/CustomerList.vue'
// ЗАГОТОВКА:
// import ProductList from './components/ProductList.vue'

const currentView = ref('users')
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
</style>