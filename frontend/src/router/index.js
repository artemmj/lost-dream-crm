import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../components/Dashboard.vue'
import UserList from '../components/UserList.vue'
import CustomerList from '../components/CustomerList.vue'

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true } // Требует авторизации
    },
    {
        path: '/users',
        name: 'Users',
        component: UserList,
        meta: { requiresAuth: true }
    },
    {
        path: '/customers',
        name: 'Customers',
        component: CustomerList,
        meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Глобальный хук перед каждым переходом
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    
    // Если маршрут требует авторизации, а токена нет
    if (to.meta.requiresAuth && !token) {
        // Разрешаем переход, но App.vue сам покажет AuthPage из-за проверки isAuthenticated
        // Или можно сделать редирект на специальную страницу, если она есть
        next() 
    } else {
        next()
    }
})

export default router
