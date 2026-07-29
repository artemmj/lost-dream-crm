import { crmApiClient } from './client'

export const authApi = {
    /**
     * POST /api/v1/crm/auth/register
     * @param {{ email: string, password: string, first_name: string, last_name: string }} data
     */
    register(data) {
        return crmApiClient.post('/auth/register', data)
    },

    /**
     * POST /api/v1/crm/auth/login
     * @param {{ email: string, password: string }} data
     * @returns token в response.data (уточните поле: access_token / token / и т.д.)
     */
    login(data) {
        return crmApiClient.post('/auth/login', data)
    },

    /**
     * GET /api/v1/crm/users/me
     * Требует заголовок Authorization с JWT
     */
    getMe() {
        return crmApiClient.get('/users/me')
    },

    /**
     * GET /api/v1/crm/auth/logout
     * Инвалидирует сессию на сервере.
     * Токен передаётся через заголовок Authorization (автоматически из интерсептора).
     */
    logout() {
        return crmApiClient.get('/auth/logout')
    },
}
