import axios from 'axios'

export function createApiClient(servicePath) {
    const client = axios.create({
        baseURL: servicePath,
        headers: {
            'Content-Type': 'application/json',
        },
    })

    // ===== JWT: добавляем токен в каждый запрос =====
    client.interceptors.request.use((config) => {
        const token = localStorage.getItem('token')
        if (token) {
            // Бэк ожидает токен БЕЗ префикса "Bearer"
            config.headers.Authorization = token
        }
        return config
    })

    // ===== JWT: обработка 401 =====
    client.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response?.status === 401) {
                localStorage.removeItem('token')

                // Не редиректим, если уже на «странице логина»
                // (в SPA без роутера просто перезагрузим — App.vue покажет AuthPage)
                const authStore = useAuthStore()
                authStore.clearLocal?.()  // если экспортировали

                // Или просто:
                // window.location.reload()
            }
            return Promise.reject(error)
        }
    )

    return client
}

export const crmApiClient = createApiClient('/api/v1/crm')
export const customersApiClient = createApiClient('/api/v1/customers')

export default crmApiClient
