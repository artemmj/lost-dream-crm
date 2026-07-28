import axios from 'axios'

/**
 * Создаёт HTTP клиент для конкретного микросервиса
 * @param {string} servicePath - путь к сервису (например, '/api/v1/crm', '/api/v1/customers')
 */
export function createApiClient(servicePath) {
    const client = axios.create({
        baseURL: servicePath,
        headers: {
        'Content-Type': 'application/json',
        },
    })

    // ===== ЗАГОТОВКА ДЛЯ JWT =====
    // client.interceptors.request.use((config) => {
    //   const token = localStorage.getItem('token')
    //   if (token) {
    //     config.headers.Authorization = `Bearer ${token}`
    //   }
    //   return config
    // })
    //
    // client.interceptors.response.use(
    //   (response) => response,
    //   (error) => {
    //     if (error.response?.status === 401) {
    //       localStorage.removeItem('token')
    //       window.location.href = '/login'
    //     }
    //     return Promise.reject(error)
    //   }
    // )

    return client
}

// Готовые клиенты для сервисов
export const crmApiClient = createApiClient('/api/v1/crm')
export const customersApiClient = createApiClient('/api/v1/customers')

// Дефолтный экспорт для обратной совместимости
export default crmApiClient
