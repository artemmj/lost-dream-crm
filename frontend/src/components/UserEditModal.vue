<template>
    <div v-if="isVisible" class="modal-overlay">
        <div class="modal-container">
            <header class="modal-header">
                <h3>Редактирование пользователя</h3>
                <button class="close-btn" @click="$emit('close')">&times;</button>
            </header>

            <form @submit.prevent="handleSubmit" class="modal-body">
                <div class="form-group">
                    <label>Email</label>
                    <input v-model="form.email" type="email" required />
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Имя</label>
                        <input v-model="form.first_name" type="text" required />
                    </div>
                    <div class="form-group">
                        <label>Фамилия</label>
                        <input v-model="form.last_name" type="text" required />
                    </div>
                </div>

                <div class="form-group checkboxes">
                    <label><input type="checkbox" v-model="form.is_active" /> Активен</label>
                    <label><input type="checkbox" v-model="form.is_banned" /> Забанен</label>
                    <label><input type="checkbox" v-model="form.is_superuser" /> Администратор</label>
                    <label><input type="checkbox" v-model="form.is_verified" /> Верифицирован</label>
                </div>

                <p v-if="error" class="error-text">{{ error }}</p>

                <footer class="modal-footer">
                    <button type="button" @click="$emit('close')" :disabled="loading">Отмена</button>
                    <button type="submit" class="btn-primary" :disabled="loading">
                        {{ loading ? 'Сохранение...' : 'Сохранить' }}
                    </button>
                </footer>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usersApi } from '../api/users'

const props = defineProps({
    isVisible: Boolean,
    user: Object
})

const emit = defineEmits(['close', 'saved'])

const form = ref({})
const loading = ref(false)
const error = ref(null)

// Заполняем форму при открытии
watch(() => props.user, (newUser) => {
    if (newUser) {
        form.value = { 
            ...newUser,
            is_active: !!newUser.is_active,
            is_banned: !!newUser.is_banned,
            is_superuser: !!newUser.is_superuser,
            is_verified: !!newUser.is_verified
        }
    }
}, { immediate: true })

async function handleSubmit() {
    loading.value = true
    error.value = null
    
    try {
        await usersApi.updateUser(props.user.id, form.value)
        emit('saved')
        emit('close')
    } catch (err) {
        if (err.response?.data?.detail) {
            error.value = Array.isArray(err.response.data.detail) 
                ? err.response.data.detail.map(d => d.msg).join(', ') 
                : err.response.data.detail
        } else {
            error.value = 'Ошибка сети или сервера'
        }
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
/* Затемненный фон на весь экран */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999; /* Гарантируем, что будет поверх всего */
}

/* Само белое окно */
.modal-container {
    background: white;
    padding: 24px;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-row {
    display: flex;
    gap: 16px;
}

.form-row .form-group {
    flex: 1;
}

input[type="text"], input[type="email"] {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
}

.checkboxes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.checkboxes label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    cursor: pointer;
}

.error-text {
    color: #dc2626;
    font-size: 14px;
    margin-top: 8px;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
}

.modal-footer button {
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    border: 1px solid #d1d5db;
    background: white;
}

.btn-primary {
    background: none;
    background: #676774;
}

.btn-primary:hover:not(:disabled) {
    color: white;
    background: #4947cf;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
}
</style>
