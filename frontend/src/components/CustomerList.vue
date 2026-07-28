<template>
    <div class="customer-list">
        <div class="customer-list__header">
            <h2>Customers</h2>
            <span class="badge">Microservice: /api/v1/customers</span>
        </div>

        <div v-if="loading" class="customer-list__loading">Loading...</div>

        <div v-else-if="error" class="customer-list__error">
            {{ error }}
            <button @click="loadCustomers">Retry</button>
        </div>

        <div v-else class="customer-list__grid">
            <div v-for="customer in customers" :key="customer.id" class="customer-card">
                <strong>{{ customer.first_name }} {{ customer.last_name }}</strong>
                <span>{{ customer.email }}</span>
            </div>
        </div>

        <div v-if="!loading && customers.length === 0" class="customer-list__empty">
            No customers found
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
import { customersApi } from '@/api'
import { useApi } from '@/composables/useApi'
import Pagination from './Pagination.vue'

const customers = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(10)

const { loading, error, execute: apiExecute } = useApi(customersApi.getCustomers)

async function loadCustomers() {
    try {
        const data = await apiExecute({
            page: currentPage.value,
            per_page: perPage.value,
        })
        customers.value = data.customers || data.items || []
        total.value = data.total || 0
    } catch (err) {
        // handled by useApi
    }
}

function changePage(page) {
    currentPage.value = page
    loadCustomers()
}

onMounted(() => {
    loadCustomers()
})
</script>

<style scoped>
.customer-list { max-width: 800px; margin: 0 auto; }
.customer-list__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.customer-list__header h2 { margin: 0; font-size: 24px; color: #1f2937; }
.customer-list__grid { display: flex; flex-direction: column; gap: 12px; }
.customer-card { padding: 16px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; }
.customer-list__loading, .customer-list__error, .customer-list__empty { text-align: center; padding: 48px; color: #6b7280; }
.customer-list__error { color: #991b1b; }
.badge { background: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
</style>
