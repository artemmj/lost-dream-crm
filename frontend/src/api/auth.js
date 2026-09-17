import { authApiClient } from './client'

export const authApi = {
    /**
     * POST /api/v1/auth/register
     * @param {{ email: string, password: string, first_name: string, last_name: string }} data
     */
    register(data) {
        return authApiClient.post('/auth/register', data)
    },

    /**
     * POST /api/v1/auth/login
     * @param {{ email: string, password: string }} data
     * @returns { access_token } в response.data
     */
    login(data) {
        return authApiClient.post('/auth/login', data)
    },

    /**
     * GET /api/v1/auth/me
     * Требует заголовок Authorization с JWT
     */
    getMe() {
        return authApiClient.get('/me')
    },

    /**
     * GET /api/v1/auth/logout
     * Инвалидирует сессию на сервере.
     * Токен передаётся через заголовок Authorization (автоматически из интерсептора).
     */
    logout() {
        return authApiClient.get('/auth/logout')
    },
}
