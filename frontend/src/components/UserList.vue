<template>
    <div class="user-list">
        <div class="user-list__header">
            <h2>Users (CRM)</h2>
            <div class="user-list__filters">
                <select v-model="filterActive" @change="loadUsers">
                <option :value="null">All users</option>
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
                </select>
            </div>
        </div>

        <div v-if="loading" class="user-list__loading">Loading...</div>

        <div v-else-if="error" class="user-list__error">
            {{ error }}
            <button @click="loadUsers">Retry</button>
        </div>

        <div v-else class="user-list__grid">
            <UserCard
                v-for="user in users"
                :key="user.id"
                :user="user"
                @edit="handleEdit"
                @deactivate="handleDeactivate"
                @activate="handleActivate"
            />
        </div>

        <div v-if="!loading && users.length === 0" class="user-list__empty">
            No users found
        </div>

        <Pagination
            :current-page="currentPage"
            :total-items="total"
            :per-page="perPage"
            @page-change="changePage"
        />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api'
import { useApi } from '@/composables/useApi'
import UserCard from './UserCard.vue'
import Pagination from './Pagination.vue'

const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(10)
const filterActive = ref(null)

const { loading, error, execute: apiExecute } = useApi(usersApi.getUsers)

async function loadUsers() {
    const params = {
        page: currentPage.value,
        per_page: perPage.value,
    }
    
    if (filterActive.value !== null) {
        params.is_active = filterActive.value
    }
    
    try {
        const data = await apiExecute(params)
        users.value = data.users
        total.value = data.total
    } catch (err) {
        // handled by useApi
    }
}

function changePage(page) {
    currentPage.value = page
    loadUsers()
}

function handleEdit(user) {
    console.log('Edit user:', user)
    alert(`Edit ${user.first_name} ${user.last_name} — coming soon`)
}

async function handleDeactivate(userId) {
    if (!confirm('Are you sure you want to deactivate this user?')) return
    
    try {
        await usersApi.deactivateUser(userId)
        await loadUsers()
    } catch (err) {
        console.error('Failed to deactivate user:', err)
        alert('Failed to deactivate user')
    }
}

async function handleActivate(userId) {
    try {
        await usersApi.activateUser(userId)
        await loadUsers()
    } catch (err) {
        console.error('Failed to activate user:', err)
        alert('Failed to activate user')
    }
}

onMounted(() => {
    loadUsers()
})
</script>

<style scoped>
.user-list { max-width: 800px; margin: 0 auto; }
.user-list__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.user-list__header h2 { margin: 0; font-size: 24px; color: #1f2937; }
.user-list__filters select { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
.user-list__grid { display: flex; flex-direction: column; gap: 12px; }
.user-list__loading, .user-list__error, .user-list__empty { text-align: center; padding: 48px 24px; color: #6b7280; font-size: 16px; }
.user-list__error { color: #991b1b; }
.user-list__error button { margin-left: 8px; padding: 4px 12px; border: 1px solid #991b1b; border-radius: 4px; background: white; color: #991b1b; cursor: pointer; }
</style>
