<template>
    <div class="dashboard">
        <section class="dashboard__welcome">
            <h2 class="dashboard__title">Kafka Demo Stream</h2>
            <p class="dashboard__subtitle">Наблюдайте, как реальные события проходят через Kafka, Schema Registry и SSE.</p>
        </section>

        <div class="dashboard__status">
            <div class="dashboard__status-indicator" :class="{ online: streamConnected }"></div>
            <span>{{ streamConnected ? 'Live-соединение активно' : 'Ожидание подключения...' }}</span>
            <span class="dashboard__counter">{{ events.length }} событий</span>
        </div>

        <div class="dashboard__controls">
            <button class="dashboard__btn dashboard__btn--primary" @click="emitCreatedEvent">
                Отправить customer.created.v1
            </button>
            <button class="dashboard__btn dashboard__btn--secondary" @click="emitUpdatedEvent">
                Отправить customer.updated.v1
            </button>
        </div>

        <div class="dashboard__grid">
            <div class="dashboard__card">
                <div class="dashboard__card-icon">👥</div>
                <h3 class="dashboard__card-title">Пользователи</h3>
                <p class="dashboard__card-desc">Управление доступами и ролями сотрудников</p>
                <button class="dashboard__card-btn" @click="goToUsers">Перейти</button>
            </div>

            <div class="dashboard__card">
                <div class="dashboard__card-icon">🏢</div>
                <h3 class="dashboard__card-title">Клиенты</h3>
                <p class="dashboard__card-desc">База клиентов и история взаимодействий</p>
                <button class="dashboard__card-btn" @click="goToCustomers">Перейти</button>
            </div>

            <div class="dashboard__card">
                <div class="dashboard__card-icon">🛡️</div>
                <h3 class="dashboard__card-title">Роли и разрешения</h3>
                <p class="dashboard__card-desc">Роли и разрешения</p>
                <button class="dashboard__card-btn" @click="goToPerms">Перейти</button>
            </div>
        </div>

        <section class="dashboard__events">
            <div class="dashboard__events-header">
                <h3>Живой поток событий</h3>
                <button class="dashboard__btn dashboard__btn--ghost" @click="events = []">Очистить</button>
            </div>

            <div v-if="!events.length" class="dashboard__empty">
                События пока не получены. Нажмите кнопку запуска для тестового события.
            </div>

            <article v-for="event in events" :key="event.id || event.event_id || event.offset" class="event-card">
                <div class="event-card__top">
                    <span class="event-card__type">{{ event.event_type }}</span>
                    <span class="event-card__source">{{ event.source || 'kafka' }}</span>
                </div>
                <div class="event-card__meta">
                    <span>topic: {{ event.topic || 'customer.events.v1' }}</span>
                    <span>offset: {{ event.offset ?? '—' }}</span>
                    <span>{{ formatTime(event.timestamp || event.payload?.created_at || event.payload?.updated_at) }}</span>
                </div>
                <pre>{{ JSON.stringify(event.payload, null, 2) }}</pre>
            </article>
        </section>
    </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { customersApiClient } from '../api/client'

const authStore = useAuthStore()
const router = useRouter()
const events = ref([])
const streamConnected = ref(false)
let stream = null

function formatTime(value) {
    if (!value) return '—'
    return new Date(value).toLocaleString('ru-RU')
}

function setupStream() {
    stream = new EventSource('/api/v1/customers/events')
    stream.onopen = () => {
        streamConnected.value = true
    }
    stream.onmessage = (event) => {
        const payload = JSON.parse(event.data)
        events.value = [{ id: crypto.randomUUID(), ...payload }, ...events.value].slice(0, 25)
    }
    stream.onerror = () => {
        streamConnected.value = false
    }
}

async function emitCreatedEvent() {
    await customersApiClient.post('/demo/customer-created')
}

async function emitUpdatedEvent() {
    await customersApiClient.post('/demo/customer-updated')
}

function goToUsers() {
    router.push('/users')
}

function goToCustomers() {
    router.push('/customers')
}

function goToPerms() {
    router.push('/perms')
}

onMounted(() => {
    setupStream()
})

onBeforeUnmount(() => {
    stream?.close()
})
</script>

<style scoped>
.dashboard__welcome { margin-bottom: 12px; }
.dashboard__title { font-size: 28px; font-weight: 700; color: #111827; margin-bottom: 8px; }
.dashboard__subtitle { color: #6b7280; }
.dashboard__status { display: flex; align-items: center; gap: 12px; font-size: 14px; color: #374151; background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 16px; margin-bottom: 20px; }
.dashboard__status-indicator { width: 10px; height: 10px; border-radius: 50%; background: #f59e0b; }
.dashboard__status-indicator.online { background: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, .5); }
.dashboard__counter { margin-left: auto; font-weight: 600; }
.dashboard__controls { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
.dashboard__btn { border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
.dashboard__btn--primary { background: #4f46e5; color: white; }
.dashboard__btn--secondary { background: #0f766e; color: white; }
.dashboard__btn--ghost { background: #f3f4f6; color: #374151; }
.dashboard__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
.dashboard__card { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; gap: 12px; transition: box-shadow 0.2s, transform 0.2s; }
.dashboard__card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); transform: translateY(-2px); }
.dashboard__card-icon { font-size: 32px; }
.dashboard__card-title { font-size: 18px; font-weight: 600; color: #1f2937; }
.dashboard__card-desc { font-size: 14px; color: #6b7280; line-height: 1.5; flex: 1; }
.dashboard__card-btn { align-self: flex-start; padding: 8px 16px; background: #4f46e5; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; transition: background 0.2s; }
.dashboard__card-btn:hover { background: #4338ca; }
.dashboard__events { margin-top: 32px; background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; }
.dashboard__events-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.dashboard__empty { text-align: center; padding: 40px; color: #6b7280; border: 1px dashed #d1d5db; border-radius: 8px; }
.event-card { padding: 16px; border: 1px solid #e5e7eb; border-radius: 10px; margin-bottom: 12px; }
.event-card__top, .event-card__meta { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.event-card__type { font-weight: 700; color: #4338ca; }
.event-card__source { font-size: 12px; padding: 3px 8px; border-radius: 999px; background: #eef2ff; color: #4338ca; }
.event-card__meta { font-size: 12px; color: #6b7280; margin-top: 8px; }
.event-card pre { margin: 12px 0 0; white-space: pre-wrap; font-size: 12px; color: #374151; background: #f9fafb; padding: 12px; border-radius: 8px; overflow-x: auto; }
</style>