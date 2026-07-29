<template>
    <div class="dashboard">
        <section class="dashboard__welcome">
            <h2 class="dashboard__title">
                Добро пожаловать, {{ authStore.currentUser?.first_name }}! 👋
            </h2>
            <p class="dashboard__subtitle">
                Выберите раздел в меню выше для начала работы с CRM системой.
            </p>
        </section>

        <div class="dashboard__grid">
            <div class="dashboard__card">
                <div class="dashboard__card-icon">👥</div>
                <h3 class="dashboard__card-title">Пользователи</h3>
                <p class="dashboard__card-desc">Управление доступами и ролями сотрудников</p>
                <button class="dashboard__card-btn" @click="goToUsers">
                    Перейти
                </button>
            </div>

            <div class="dashboard__card">
                <div class="dashboard__card-icon">🏢</div>
                <h3 class="dashboard__card-title">Клиенты</h3>
                <p class="dashboard__card-desc">База клиентов и история взаимодействий</p>
                <button class="dashboard__card-btn" @click="goToCustomers">
                    Перейти
                </button>
            </div>

            <div class="dashboard__card dashboard__card--placeholder">
                <div class="dashboard__card-icon">📊</div>
                <h3 class="dashboard__card-title">Аналитика</h3>
                <p class="dashboard__card-desc">Отчеты и метрики (скоро)</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

function goToUsers() {
    router.push('/users')
}

function goToCustomers() {
    router.push('/customers')
}
</script>

<style scoped>
/* Стили остаются прежними */
.dashboard__welcome { margin-bottom: 32px; }
.dashboard__title { font-size: 28px; font-weight: 700; color: #111827; margin-bottom: 8px; }
.dashboard__subtitle { font-size: 16px; color: #6b7280; }
.dashboard__grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px;
}
.dashboard__card {
    background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px;
    display: flex; flex-direction: column; gap: 12px; transition: box-shadow 0.2s, transform 0.2s;
}
.dashboard__card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); transform: translateY(-2px); }
.dashboard__card--placeholder { opacity: 0.6; pointer-events: none; }
.dashboard__card-icon { font-size: 32px; }
.dashboard__card-title { font-size: 18px; font-weight: 600; color: #1f2937; }
.dashboard__card-desc { font-size: 14px; color: #6b7280; line-height: 1.5; flex: 1; }
.dashboard__card-btn {
    align-self: flex-start; padding: 8px 16px; background: #4f46e5; color: white;
    border: none; border-radius: 6px; font-size: 14px; cursor: pointer; transition: background 0.2s;
}
.dashboard__card-btn:hover { background: #4338ca; }
</style>