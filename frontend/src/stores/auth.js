import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    // ===== State =====
    const token = ref(localStorage.getItem('token') || null)
    const user = ref(null)

    // ===== Getters =====
    const isAuthenticated = computed(() => !!token.value)
    const currentUser = computed(() => user.value)

    // ===== Actions =====
    // ЗАГОТОВКА: будет реализовано когда появится эндпоинт /auth/login
    async function login(email, password) {
        // const response = await apiClient.post('/auth/login', { email, password })
        // token.value = response.data.access_token
        // localStorage.setItem('token', token.value)
        // user.value = response.data.user
        throw new Error('Auth not implemented yet')
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    return {
        token,
        user,
        isAuthenticated,
        currentUser,
        login,
        logout,
    }
})
