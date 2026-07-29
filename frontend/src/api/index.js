// Экспортируем все API модули из одного места
export { usersApi } from './users'
export { customersApi } from './customers'
export { authApi } from './auth'
export { crmApiClient, customersApiClient, createApiClient } from './client'

/**
 * ЗАГОТОВКА: Добавление новых микросервисов
 * 
 * 1. Создать файл src/api/новый-сервис.js
 * 2. Импортировать нужный клиент из './client'
 * 3. Экспортировать API объект
 * 4. Добавить экспорт в этот файл
 * 
 * Пример:
 * export { productsApi } from './products'
 * export { ordersApi } from './orders'
*/
