<template>
    <div class="auth-page">
        <div class="auth-card">
            <h2 class="auth-card__title">CRM System</h2>

            <!-- Переключатель Логин / Регистрация -->
            <div class="auth-card__tabs">
                <button
                    :class="{ active: mode === 'login' }"
                    @click="mode = 'login'"
                >
                    Login
                </button>
                <button
                    :class="{ active: mode === 'register' }"
                    @click="mode = 'register'"
                >
                    Register
                </button>
            </div>

            <!-- Сообщение об ошибке -->
            <p v-if="authStore.error" class="auth-card__error">
                {{ authStore.error }}
            </p>

            <!-- ===== Форма логина ===== -->
            <form
                v-if="mode === 'login'"
                class="auth-card__form"
                @submit.prevent="handleLogin"
            >
                <label>
                    Email
                    <input
                        v-model="loginForm.email"
                        type="email"
                        placeholder="test@test.com"
                        required
                    />
                </label>

                <label>
                    Password
                    <input
                        v-model="loginForm.password"
                        type="password"
                        placeholder="••••••••"
                        required
                    />
                </label>

                <button type="submit" :disabled="authStore.loading">
                    {{ authStore.loading ? 'Signing in…' : 'Sign In' }}
                </button>
            </form>

            <!-- ===== Форма регистрации ===== -->
            <form
                v-else
                class="auth-card__form"
                @submit.prevent="handleRegister"
            >
                <label>
                    First Name
                    <input
                        v-model="registerForm.first_name"
                        type="text"
                        placeholder="John"
                        required
                    />
                </label>

                <label>
                    Last Name
                    <input
                        v-model="registerForm.last_name"
                        type="text"
                        placeholder="Doe"
                        required
                    />
                </label>

                <label>
                    Email
                    <input
                        v-model="registerForm.email"
                        type="email"
                        placeholder="test@test.com"
                        required
                    />
                </label>

                <label>
                    Password
                    <input
                        v-model="registerForm.password"
                        type="password"
                        placeholder="мин. 8 символов"
                        minlength="8"
                        required
                    />
                </label>

                <button type="submit" :disabled="authStore.loading">
                    {{ authStore.loading ? 'Creating account…' : 'Sign Up' }}
                </button>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const mode = ref('login') // 'login' | 'register'

const loginForm = reactive({
    email: '',
    password: '',
})

const registerForm = reactive({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
})

async function handleLogin() {
    try {
        await authStore.login(loginForm.email, loginForm.password)
    } catch {
        // ошибка уже в authStore.error
    }
}

async function handleRegister() {
    try {
        await authStore.register({ ...registerForm })
    } catch {
        // ошибка уже в authStore.error
    }
}
</script>

<style scoped>
.auth-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f0f2f5;
}

.auth-card {
    background: #fff;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.auth-card__title {
    text-align: center;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

.auth-card__tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.auth-card__tabs button {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    background: #fafafa;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.auth-card__tabs button.active {
    background: #1a73e8;
    color: #fff;
    border-color: #1a73e8;
}

.auth-card__error {
    color: #d32f2f;
    background: #fdecea;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-size: 0.875rem;
}

.auth-card__form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.auth-card__form label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
}

.auth-card__form input {
    padding: 0.6rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
}

.auth-card__form input:focus {
    outline: none;
    border-color: #1a73e8;
    box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
}

.auth-card__form button[type="submit"] {
    padding: 0.7rem;
    background: #1a73e8;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}

.auth-card__form button[type="submit"]:hover:not(:disabled) {
    background: #1557b0;
}

.auth-card__form button[type="submit"]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>
