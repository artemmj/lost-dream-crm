import { customersApiClient } from './client'

export const customersApi = {
    getCustomers(params = {}) {
        return customersApiClient.get('/customers/', { params })
    },

    getCustomer(id) {
        return customersApiClient.get(`/customers/${id}`)
    },

    createCustomer(data) {
        return customersApiClient.post('/customers/', data)
    },

    updateCustomer(id, data) {
        return customersApiClient.patch(`/customers/${id}`, data)
    },

    deleteCustomer(id) {
        return customersApiClient.delete(`/customers/${id}`)
    },

    searchCustomers(query) {
        return customersApiClient.get('/customers/search', { params: { q: query } })
    },

    getCustomersStats() {
        return customersApiClient.get('/customers/stats')
    },
}
