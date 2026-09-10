<template>
    <div class="user-card" :class="{ 'user-card--inactive': !user.is_active }">
        <div class="user-card__avatar">
            {{ initials }}
        </div>
        <div class="user-card__info">
            <div class="user-card__name">{{ user.first_name }} {{ user.last_name }}</div>
            <div class="user-card__email">{{ user.email }}</div>
            <div class="user-card__badges">
                <span v-if="user.is_superuser" class="badge badge--superuser">Админ</span>
                <span v-if="user.is_verified" class="badge badge--verified">Верифицирован</span>
                <span v-if="user.is_banned" class="badge badge--banned">Забанен</span>
                <span v-if="!user.is_active" class="badge badge--inactive">Неактивен</span>
            </div>
            <!-- Блок вывода ролей -->
            <div class="user-card__roles">
                <div v-if="user.roles && user.roles.length > 0" class="roles-list">
                    <span class="roles-label">Роли:</span>
                    <span 
                        v-for="role in user.roles" 
                        :key="role.id"
                        class="role-tag"
                        :title="role.permissions && role.permissions.length > 0 
                            ? 'Права: ' + role.permissions.map(p => p.description).join(', ')
                            : 'Нет прав'"
                    >
                        {{ role.name }}
                        <span v-if="role.permissions && role.permissions.length > 0" class="permissions-count">
                            ({{ role.permissions.length }})
                        </span>
                    </span>
                </div>
                <span v-else class="no-roles">Нет ролей</span>
            </div>
        </div>
        <div class="user-card__actions">
            <button class="btn btn--small" @click="$emit('edit', user)">
                ✏️
            </button>
            <button class="btn btn--roles" @click="openRolesModal">
                👥
            </button>
            <button class="btn btn--delete" @click="$emit('delete', user.id)">
                🗑️
            </button>
        </div>
    </div>

    <!-- Модалка редактирования ролей -->
    <div v-if="showRolesModal" class="roles-modal__overlay" @click.self="closeRolesModal">
        <div class="roles-modal">
            <div class="roles-modal__header">
                <h3>Редактирование ролей</h3>
                <button class="roles-modal__close" @click="closeRolesModal">×</button>
            </div>
            <div class="roles-modal__body">
                <p class="roles-modal__user">{{ user.first_name }} {{ user.last_name }} ({{ user.email }})</p>
                
                <div v-if="rolesLoading" class="roles-modal__loading">Загрузка ролей...</div>
                <div v-else-if="allRoles.length === 0" class="roles-modal__empty">Нет доступных ролей</div>
                <div v-else class="roles-modal__list">
                    <label v-for="role in allRoles" :key="role.id" class="roles-modal__item">
                        <input 
                            type="checkbox" 
                            :value="role.id" 
                            v-model="selectedRoleIds" 
                        />
                        <div class="roles-modal__item-info">
                            <span class="roles-modal__item-name">{{ role.name }}</span>
                            <span v-if="role.permissions?.length" class="roles-modal__item-perms">
                                ({{ role.permissions.length }} прав)
                            </span>
                        </div>
                    </label>
                </div>
                
                <p v-if="rolesError" class="roles-modal__error">{{ rolesError }}</p>
            </div>
            <div class="roles-modal__footer">
                <button class="roles-modal__btn roles-modal__btn--secondary" @click="closeRolesModal">
                    Отмена
                </button>
                <button 
                    class="roles-modal__btn roles-modal__btn--primary" 
                    :disabled="rolesSaving" 
                    @click="saveRoles"
                >
                    {{ rolesSaving ? 'Сохранение...' : 'Сохранить' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { permsApi } from '@/api'

const props = defineProps({
    user: {
        type: Object,
        required: true,
    },
})

const emit = defineEmits(['edit', 'delete', 'roles-updated'])

const initials = computed(() => {
    return `${props.user.first_name?.[0] || ''}${props.user.last_name?.[0] || ''}`.toUpperCase()
})

// ==================== STATE ====================
const showRolesModal = ref(false)
const allRoles = ref([])
const selectedRoleIds = ref([])
const rolesLoading = ref(false)
const rolesSaving = ref(false)
const rolesError = ref('')

// ==================== METHODS ====================
async function openRolesModal() {
    showRolesModal.value = true
    rolesError.value = ''
    await fetchAllRoles()
    // Заполняем выбранные роли из текущего пользователя
    selectedRoleIds.value = props.user.roles?.map(r => r.id) || []
}

function closeRolesModal() {
    showRolesModal.value = false
    rolesError.value = ''
}

async function fetchAllRoles() {
    rolesLoading.value = true
    try {
        const { data } = await permsApi.getRoles({ per_page: 99 })
        allRoles.value = data.items || []
    } catch (e) {
        console.error('Failed to fetch roles:', e)
        rolesError.value = 'Ошибка загрузки ролей'
    } finally {
        rolesLoading.value = false
    }
}

async function saveRoles() {
    rolesSaving.value = true
    rolesError.value = ''
    try {
        await permsApi.assignUserRoles(props.user.id, selectedRoleIds.value)

        // Обновляем пользователя в родительском компоненте
        emit('roles-updated', {
            userId: props.user.id,
            roleIds: selectedRoleIds.value,
        })
        closeRolesModal()
    } catch (e) {
        rolesError.value = e.response?.data?.detail || e.message || 'Ошибка сохранения ролей'
    } finally {
        rolesSaving.value = false
    }
}
</script>

<style scoped>
/* Существующие стили */
.user-card{display:flex;align-items:center;gap:16px;padding:16px;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.1);transition:box-shadow .2s}
.user-card:hover{box-shadow:0 2px 8px rgba(0,0,0,.15)}
.user-card--inactive{opacity:.6}
.user-card__avatar{width:40px;height:40px;border-radius:50%;background:#4f46e5;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:14px;flex-shrink:0}
.user-card--inactive .user-card__avatar{background:#9ca3af}
.user-card__info{flex:1;min-width:0}
.user-card__name{font-weight:600;color:#1f2937}
.user-card__email{color:#6b7280;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.user-card__badges{display:flex;gap:4px;margin-top:4px;flex-wrap:wrap}
.badge{padding:2px 8px;border-radius:12px;font-size:11px;font-weight:500}
.badge--superuser{background:#fef3c7;color:#92400e}
.badge--verified{background:#d1fae5;color:#065f46}
.badge--banned{background:#fee2e2;color:#991b1b}
.badge--inactive{background:#f3f4f6;color:#6b7280}
.user-card__roles{margin-top:6px}
.roles-list{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.roles-label{font-size:12px;color:#6b7280;font-weight:500}
.role-tag{background:#e0e7ff;color:#3730a3;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500;display:inline-flex;align-items:center;gap:2px;cursor:help;transition:background .2s}
.role-tag:hover{background:#c7d2fe}
.permissions-count{font-size:10px;opacity:.7}
.no-roles{font-size:12px;color:#9ca3af;font-style:italic}
.user-card__actions{display:flex;gap:8px;flex-shrink:0}
.btn{padding:6px 12px;border:none;border-radius:6px;cursor:pointer;font-size:13px;transition:background .2s}
.btn--small{padding:4px 10px;font-size:12px;background:#e0e7ff;color:#3730a3}
.btn--small:hover{background:#c7d2fe}
.btn--roles{padding:4px 10px;font-size:12px;background:#fef3c7;color:#92400e;border:1px solid #fde68a}
.btn--roles:hover{background:#fde68a}
.btn--delete{background-color:#fee2e2;color:#dc2626;border:1px solid #fca5a5}
.btn--delete:hover{background-color:#dc2626;color:#fff;border-color:#dc2626}

/* Стили модалки */
.roles-modal__overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center;animation:fadeIn .2s}
.roles-modal{background:#fff;border-radius:12px;width:480px;max-width:90vw;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.3);animation:slideUp .2s}
.roles-modal__header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid #e5e7eb}
.roles-modal__header h3{font-size:18px;font-weight:600;color:#111827;margin:0}
.roles-modal__close{background:none;border:none;font-size:24px;color:#6b7280;cursor:pointer;padding:0 4px;transition:color .2s}
.roles-modal__close:hover{color:#111827}
.roles-modal__body{padding:20px 24px;overflow-y:auto;flex:1}
.roles-modal__user{font-size:14px;color:#6b7280;margin-bottom:16px;padding:8px 12px;background:#f9fafb;border-radius:6px}
.roles-modal__loading,.roles-modal__empty{text-align:center;color:#9ca3af;padding:24px 0}
.roles-modal__list{display:flex;flex-direction:column;gap:4px;max-height:300px;overflow-y:auto}
.roles-modal__item{display:flex;align-items:center;gap:12px;padding:8px 12px;border-radius:6px;cursor:pointer;transition:background .15s}
.roles-modal__item:hover{background:#f9fafb}
.roles-modal__item input[type="checkbox"]{width:18px;height:18px;accent-color:#4f46e5;cursor:pointer;flex-shrink:0}
.roles-modal__item-info{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.roles-modal__item-name{font-size:14px;font-weight:500;color:#1f2937}
.roles-modal__item-perms{font-size:12px;color:#6b7280}
.roles-modal__error{color:#dc2626;font-size:13px;margin-top:12px;padding:8px 12px;background:#fef2f2;border-radius:6px}
.roles-modal__footer{display:flex;gap:8px;justify-content:flex-end;padding:16px 24px;border-top:1px solid #e5e7eb}
.roles-modal__btn{padding:8px 20px;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:500;transition:all .2s}
.roles-modal__btn--secondary{background:#f3f4f6;color:#6b7280}
.roles-modal__btn--secondary:hover{background:#e5e7eb}
.roles-modal__btn--primary{background:#4f46e5;color:#fff}
.roles-modal__btn--primary:hover{background:#4338ca}
.roles-modal__btn--primary:disabled{opacity:.6;cursor:not-allowed}

@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
</style>
