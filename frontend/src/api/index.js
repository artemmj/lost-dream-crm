/**
 * src/api/index.js
 * 
 * Центральная точка экспорта для всех API-клиентов и модулей.
 * Позволяет импортировать всё из одного места: import { authApi, usersApi } from '@/api'
 */

// ===== 1. Базовые клиенты (HTTP instances) =====
export { 
    createApiClient, 
    crmApiClient,      // Для сервисов внутри /api/v1/crm/...
    customersApiClient // Для внешнего сервиса /api/v1/customers/...
} from './client'

// ===== 2. Модули API (Бизнес-логика запросов) =====
export { authApi } from './auth'
export { usersApi } from './users'
export { customersApi } from './customers'

// ===== ЗАГОТОВКА: Добавление новых микросервисов =====
/*
 * Алгоритм добавления нового сервиса:
 * 
 * 1. Создать файл src/api/new-service.js
 *    - Импортировать нужный клиент из './client' (или создать новый через createApiClient)
 *    - Экспортировать объект с методами API
 * 
 * 2. Добавить экспорт в этот файл:
 *    export { newServiceApi } from './new-service'
 * 
 * Пример структуры нового файла (src/api/products.js):
 * 
 * import { crmApiClient } from './client'
 * 
 * export const productsApi = {
 *   getList(params) {
 *     return crmApiClient.get('/products', { params })
 *   },
 *   getById(id) {
 *     return crmApiClient.get(`/products/${id}`)
 *   },
 *   create(data) {
 *     return crmApiClient.post('/products', data)
 *   }
 * }
 */

// Примеры для будущего использования:
// export { productsApi } from './products'
// export { ordersApi } from './orders'
// export { analyticsApi } from './analytics'
