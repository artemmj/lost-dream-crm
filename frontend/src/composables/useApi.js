import { ref } from 'vue'

/**
 * Composable для работы с любым API
 * @param {Function} apiCall - функция API вызова
 * @returns {{ data, loading, error, execute }}
 * 
 * @example
 * const { data: users, loading, execute: loadUsers } = useApi(() => usersApi.getUsers({ page: 1 }))
 */
export function useApi(apiCall) {
    const data = ref(null)
    const loading = ref(false)
    const error = ref(null)

    async function execute(...args) {
        loading.value = true
        error.value = null
        
        try {
            const response = await apiCall(...args)
            data.value = response.data
            return response.data
        } catch (err) {
            error.value = err.response?.data?.detail || err.message || 'Request failed'
            console.error('API Error:', err)
            throw err
        } finally {
            loading.value = false
        }
    }

    return { data, loading, error, execute }
}