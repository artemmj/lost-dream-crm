// src/api/perms.js
import { crmApiClient } from './client'

export const permsApi = {
    // ==================== PERMISSIONS ====================

    getPermissions(params = {}) {
        return crmApiClient.get('/perms/permissions', { params })
    },

    createPermission(data) {
        return crmApiClient.post('/perms/permissions', data)
    },

    updatePermission(id, data) {
        return crmApiClient.patch(`/perms/permissions/${id}`, data)
    },

    deletePermission(id) {
        return crmApiClient.delete(`/perms/permissions/${id}`)
    },

    // ==================== ROLES ====================

    getRoles(params = {}) {
        return crmApiClient.get('/perms/roles', { params })
    },

    createRole(data) {
        return crmApiClient.post('/perms/roles', data)
    },

    updateRole(id, data) {
        return crmApiClient.patch(`/perms/roles/${id}`, data)
    },

    deleteRole(id) {
        return crmApiClient.delete(`/perms/roles/${id}`)
    },

    // ==================== USER ROLES ====================

    // getUserRoles(userId) {
    //     return crmApiClient.get(`/perms/users/${userId}/roles`)
    // },

    assignUserRoles(userId, roleIds) {
        return crmApiClient.put(`/perms/users/${userId}/roles`, { role_ids: roleIds })
    },
}
