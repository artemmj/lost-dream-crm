import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
    // ===== State =====
    const token = ref(localStorage.getItem('token') || null)
    const user = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // ===== Getters =====
    const isAuthenticated = computed(() => !!token.value)
    const currentUser = computed(() => user.value)

    // ===== Actions =====

    /**
     * Логин. Сохраняет токен и подтягивает профиль.
     */
    async function login(email, password) {
        loading.value = true
        error.value = null
        try {
            const response = await authApi.login({ email, password })

            // ⚠️ Подставьте правильное поле из ответа вашего бэка.
            // Варианты: response.data.access_token, response.data.token, response.data
            const jwt = response.data.access_token
                ?? response.data.token
                ?? response.data

            token.value = jwt
            localStorage.setItem('token', jwt)

            // Сразу подтягиваем профиль
            await fetchUser()

            return true
        } catch (err) {
            error.value = err.response?.data?.detail || err.message || 'Login failed'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Регистрация. После успешной регистрации можно сразу логиниться.
     */
    async function register({ email, password, first_name, last_name }) {
        loading.value = true
        error.value = null
        try {
            await authApi.register({ email, password, first_name, last_name })
            // Авто-логин после регистрации
            await login(email, password)
            return true
        } catch (err) {
            error.value = err.response?.data?.detail || err.message || 'Registration failed'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Получить текущего пользователя по токену.
     */
    async function fetchUser() {
        if (!token.value) return
        try {
            const response = await authApi.getMe()
            user.value = response.data
        } catch (err) {
            // Токен протух или невалиден — разлогиниваемся
            logout()
            throw err
        }
    }

    /**
     * Logout: сначала говорим серверу инвалидировать сессию,
     * потом чистим локальное состояние.
     */
    async function logout() {
        try {
            // Если токен есть — сообщаем бэку
            if (token.value) {
                await authApi.logout()
            }
        } catch (err) {
            // Даже если сервер ответил ошибкой (401, сеть и т.д.) —
            // всё равно чистим локально, чтобы пользователь не застрял
            console.warn('Server logout failed, clearing local session:', err.message)
        } finally {
            clearLocal()
        }
    }

    /**
     * Внутренняя: очистка локального состояния без обращения к API.
     */
    function clearLocal() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    /**
     * Инициализация при загрузке приложения:
     * если токен есть — подтягиваем профиль.
     */
    async function init() {
        if (token.value) {
            try {
                await fetchUser()
            } catch {
                // fetchUser уже вызовет logout
            }
        }
    }

    return {
        token,
        user,
        loading,
        error,
        isAuthenticated,
        currentUser,
        login,
        register,
        fetchUser,
        logout,
        init,
    }
})
