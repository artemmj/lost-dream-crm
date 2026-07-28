import { crmApiClient } from './client'

export const usersApi = {
    getUsers(params = {}) {
        return crmApiClient.get('/users/', { params })
    },

    getUser(id) {
        return crmApiClient.get(`/users/${id}`)
    },

    createUser(data) {
        return crmApiClient.post('/users/', data)
    },

    updateUser(id, data) {
        return crmApiClient.patch(`/users/${id}`, data)
    },

    deleteUser(id) {
        return crmApiClient.delete(`/users/${id}`)
    },

    deactivateUser(id) {
        return crmApiClient.post(`/users/${id}/deactivate`)
    },

    banUser(id) {
        return crmApiClient.post(`/users/${id}/ban`)
    },

    unbanUser(id) {
        return crmApiClient.post(`/users/${id}/unban`)
    },

    checkEmails(emails) {
        return crmApiClient.post('/users/check-emails', { emails })
    },
}
