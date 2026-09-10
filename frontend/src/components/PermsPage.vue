<template>
    <div class="perms-page">
        <h2 class="perms-page__title">Роли и разрешения</h2>

        <!-- ===== БЛОК РОЛЕЙ ===== -->
        <div class="perms-page__section">
            <div class="perms-page__section-header">
                <h3 class="perms-page__section-title">Роли</h3>
                <button class="perms-page__btn perms-page__btn--primary" @click="openRoleModal()">
                    + Новая роль
                </button>
            </div>

            <div class="perms-page__toolbar">
                <input
                    v-model="roleSearch"
                    class="perms-page__search"
                    placeholder="Поиск по названию роли..."
                    @input="debouncedFetchRoles"
                />
            </div>

            <table class="perms-page__table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Название</th>
                        <th>Пермишены</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="roleLoading">
                        <td colspan="4" class="perms-page__loading">Загрузка...</td>
                    </tr>
                    <tr v-else-if="!roles.length">
                        <td colspan="4" class="perms-page__empty">Нет ролей</td>
                    </tr>
                    <tr v-for="role in roles" :key="role.id">
                        <td>{{ role.id }}</td>
                        <td><strong>{{ role.name }}</strong></td>
                        <td>
                            <div class="perms-page__tags">
                                <span v-for="p in role.permissions" :key="p.id" class="perms-page__tag">
                                    {{ p.code }}
                                </span>
                                <span v-if="!role.permissions?.length" class="perms-page__empty-tag">нет</span>
                            </div>
                        </td>
                        <td class="perms-page__actions">
                            <button class="perms-page__btn-sm" @click="openRoleModal(role)">✏️</button>
                            <button class="perms-page__btn-sm perms-page__btn-sm--danger" @click="deleteRole(role.id)">🗑️</button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="perms-page__pagination">
                <button :disabled="rolePage <= 1" @click="changeRolePage(rolePage - 1)">← Назад</button>
                <span>Стр. {{ rolePage }} из {{ roleTotalPages }}</span>
                <button :disabled="rolePage >= roleTotalPages" @click="changeRolePage(rolePage + 1)">Вперёд →</button>
            </div>
        </div>

        <!-- ===== БЛОК ПЕРМИШЕНОВ ===== -->
        <div class="perms-page__section">
            <div class="perms-page__section-header">
                <h3 class="perms-page__section-title">Пермишены</h3>
                <button class="perms-page__btn perms-page__btn--primary" @click="openPermModal()">
                    + Новый пермишен
                </button>
            </div>

            <div class="perms-page__toolbar">
                <input
                    v-model="permSearch"
                    class="perms-page__search"
                    placeholder="Поиск по коду или описанию..."
                    @input="debouncedFetchPermissions"
                />
            </div>

            <table class="perms-page__table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Код</th>
                        <th>Описание</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="permLoading">
                        <td colspan="4" class="perms-page__loading">Загрузка...</td>
                    </tr>
                    <tr v-else-if="!permissions.length">
                        <td colspan="4" class="perms-page__empty">Нет пермишенов</td>
                    </tr>
                    <tr v-for="perm in permissions" :key="perm.id">
                        <td>{{ perm.id }}</td>
                        <td><code class="perms-page__code">{{ perm.code }}</code></td>
                        <td>{{ perm.description || '—' }}</td>
                        <td class="perms-page__actions">
                            <button class="perms-page__btn-sm" @click="openPermModal(perm)">✏️</button>
                            <button class="perms-page__btn-sm perms-page__btn-sm--danger" @click="deletePermission(perm.id)">🗑️</button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="perms-page__pagination">
                <button :disabled="permPage <= 1" @click="changePermPage(permPage - 1)">← Назад</button>
                <span>Стр. {{ permPage }} из {{ permTotalPages }}</span>
                <button :disabled="permPage >= permTotalPages" @click="changePermPage(permPage + 1)">Вперёд →</button>
            </div>
        </div>

        <!-- ===== МОДАЛКА РОЛИ ===== -->
        <div v-if="showRoleModal" class="perms-page__overlay" @click.self="showRoleModal = false">
            <div class="perms-page__modal perms-page__modal--wide">
                <h3>{{ editingRole ? 'Редактировать роль' : 'Новая роль' }}</h3>
                <label>
                    Название
                    <input v-model="roleForm.name" placeholder="moderator" />
                </label>
                <label>
                    Пермишены
                    <div class="perms-page__checkbox-list">
                        <label v-for="p in allPermissions" :key="p.id" class="perms-page__checkbox">
                            <input type="checkbox" :value="p.id" v-model="roleForm.permission_ids" />
                            <span>{{ p.code }}</span>
                            <small v-if="p.description">{{ p.description }}</small>
                        </label>
                    </div>
                </label>
                <p v-if="roleError" class="perms-page__error">{{ roleError }}</p>
                <div class="perms-page__modal-actions">
                    <button class="perms-page__btn" @click="showRoleModal = false">Отмена</button>
                    <button class="perms-page__btn perms-page__btn--primary" :disabled="roleSaving" @click="saveRole">
                        {{ roleSaving ? 'Сохранение...' : 'Сохранить' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- ===== МОДАЛКА ПЕРМИШЕНА ===== -->
        <div v-if="showPermModal" class="perms-page__overlay" @click.self="showPermModal = false">
            <div class="perms-page__modal">
                <h3>{{ editingPerm ? 'Редактировать пермишен' : 'Новый пермишен' }}</h3>
                <label>
                    Код
                    <input v-model="permForm.code" :disabled="!!editingPerm" placeholder="create_user" />
                </label>
                <label>
                    Описание
                    <input v-model="permForm.description" placeholder="Создание пользователя" />
                </label>
                <p v-if="permError" class="perms-page__error">{{ permError }}</p>
                <div class="perms-page__modal-actions">
                    <button class="perms-page__btn" @click="showPermModal = false">Отмена</button>
                    <button class="perms-page__btn perms-page__btn--primary" :disabled="permSaving" @click="savePermission">
                        {{ permSaving ? 'Сохранение...' : 'Сохранить' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { permsApi } from '@/api'

// ==================== STATE ====================
// Roles
const roles = ref([])
const roleLoading = ref(false)
const roleSearch = ref('')
const rolePage = ref(1)
const perPage = 7
const roleTotal = ref(0)

// Permissions
const permissions = ref([])
const permLoading = ref(false)
const permSearch = ref('')
const permPage = ref(1)
const permTotal = ref(0)

// All permissions (для чекбоксов в модалке роли)
const allPermissions = ref([])

// Role Modal
const showRoleModal = ref(false)
const editingRole = ref(null)
const roleForm = ref({ name: '', permission_ids: [] })
const roleSaving = ref(false)
const roleError = ref('')

// Perm Modal
const showPermModal = ref(false)
const editingPerm = ref(null)
const permForm = ref({ code: '', description: '' })
const permSaving = ref(false)
const permError = ref('')

// ==================== COMPUTED ====================
const roleTotalPages = computed(() => Math.max(1, Math.ceil(roleTotal.value / perPage)))
const permTotalPages = computed(() => Math.max(1, Math.ceil(permTotal.value / perPage)))

// ==================== DEBOUNCE ====================
let roleTimer = null
let permTimer = null

function debouncedFetchRoles() {
    clearTimeout(roleTimer)
    roleTimer = setTimeout(() => {
        rolePage.value = 1
        fetchRoles()
    }, 300)
}

function debouncedFetchPermissions() {
    clearTimeout(permTimer)
    permTimer = setTimeout(() => {
        permPage.value = 1
        fetchPermissions()
    }, 300)
}

// ==================== API CALLS ====================
async function fetchRoles() {
    roleLoading.value = true
    try {
        const { data } = await permsApi.getRoles({
            page: rolePage.value,
            per_page: perPage,
            search: roleSearch.value || undefined,
        })
        roles.value = data.items
        roleTotal.value = data.total
    } catch (e) {
        console.error('Failed to fetch roles:', e)
    } finally {
        roleLoading.value = false
    }
}

async function fetchPermissions() {
    permLoading.value = true
    try {
        const { data } = await permsApi.getPermissions({
            page: permPage.value,
            per_page: perPage,
            search: permSearch.value || undefined,
        })
        permissions.value = data.items
        permTotal.value = data.total
        // Обновляем allPermissions для чекбоксов
        allPermissions.value = data.items
    } catch (e) {
        console.error('Failed to fetch permissions:', e)
    } finally {
        permLoading.value = false
    }
}

// ==================== ROLE CRUD ====================
function openRoleModal(role = null) {
    editingRole.value = role
    roleForm.value = role
        ? { name: role.name, permission_ids: role.permissions?.map(p => p.id) || [] }
        : { name: '', permission_ids: [] }
    roleError.value = ''
    showRoleModal.value = true
}

async function saveRole() {
    roleSaving.value = true
    roleError.value = ''
    try {
        if (editingRole.value) {
            await permsApi.updateRole(editingRole.value.id, roleForm.value)
        } else {
            await permsApi.createRole(roleForm.value)
        }
        showRoleModal.value = false
        await fetchRoles()
    } catch (e) {
        roleError.value = e.response?.data?.detail || 'Ошибка сохранения'
    } finally {
        roleSaving.value = false
    }
}

async function deleteRole(id) {
    if (!confirm('Удалить эту роль? Она будет снята со всех пользователей.')) return
    try {
        await permsApi.deleteRole(id)
        await fetchRoles()
    } catch (e) {
        alert(e.response?.data?.detail || 'Ошибка удаления')
    }
}

function changeRolePage(page) {
    rolePage.value = page
    fetchRoles()
}

// ==================== PERMISSION CRUD ====================
function openPermModal(perm = null) {
    editingPerm.value = perm
    permForm.value = perm
        ? { code: perm.code, description: perm.description || '' }
        : { code: '', description: '' }
    permError.value = ''
    showPermModal.value = true
}

async function savePermission() {
    permSaving.value = true
    permError.value = ''
    try {
        if (editingPerm.value) {
            await permsApi.updatePermission(editingPerm.value.id, {
                description: permForm.value.description || null,
            })
        } else {
            await permsApi.createPermission(permForm.value)
        }
        showPermModal.value = false
        await fetchPermissions()
    } catch (e) {
        permError.value = e.response?.data?.detail || 'Ошибка сохранения'
    } finally {
        permSaving.value = false
    }
}

async function deletePermission(id) {
    if (!confirm('Удалить этот пермишен? Он будет убран из всех ролей.')) return
    try {
        await permsApi.deletePermission(id)
        await fetchPermissions()
    } catch (e) {
        alert(e.response?.data?.detail || 'Ошибка удаления')
    }
}

function changePermPage(page) {
    permPage.value = page
    fetchPermissions()
}

// ==================== INIT ====================
onMounted(async () => {
    await Promise.all([fetchRoles(), fetchPermissions()])
})
</script>

<style scoped>
.perms-page__title{font-size:28px;font-weight:700;color:#111827;margin-bottom:24px}
.perms-page__section{margin-bottom:40px}
.perms-page__section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.perms-page__section-title{font-size:20px;font-weight:600;color:#1f2937;margin:0}
.perms-page__toolbar{display:flex;gap:12px;margin-bottom:16px;align-items:center}
.perms-page__search{flex:1;max-width:400px;padding:8px 12px;border:1px solid #d1d5db;border-radius:6px;font-size:14px;outline:none;transition:border-color .2s}
.perms-page__search:focus{border-color:#4f46e5}
.perms-page__btn{padding:8px 16px;border:1px solid #d1d5db;border-radius:6px;background:#fff;cursor:pointer;font-size:14px;transition:all .2s}
.perms-page__btn:hover{background:#f3f4f6}
.perms-page__btn--primary{background:#4f46e5;color:#fff;border-color:#4f46e5}
.perms-page__btn--primary:hover{background:#4338ca}
.perms-page__btn--primary:disabled{opacity:.6;cursor:not-allowed}
.perms-page__table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb}
.perms-page__table th{text-align:left;padding:12px 16px;background:#f9fafb;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #e5e7eb}
.perms-page__table td{padding:12px 16px;border-bottom:1px solid #f3f4f6;font-size:14px}
.perms-page__table tr:last-child td{border-bottom:none}
.perms-page__table tr:hover td{background:#f9fafb}
.perms-page__loading,.perms-page__empty{text-align:center;color:#9ca3af;padding:32px!important}
.perms-page__code{background:#f3f4f6;padding:2px 8px;border-radius:4px;font-size:13px;color:#7c3aed}
.perms-page__actions{display:flex;gap:6px}
.perms-page__btn-sm{padding:4px 8px;border:1px solid #e5e7eb;border-radius:4px;background:#fff;cursor:pointer;font-size:14px;transition:all .2s}
.perms-page__btn-sm:hover{background:#f3f4f6}
.perms-page__btn-sm--danger:hover{background:#fef2f2;border-color:#fca5a5}
.perms-page__tags{display:flex;flex-wrap:wrap;gap:4px}
.perms-page__tag{background:#ede9fe;color:#7c3aed;padding:2px 8px;border-radius:4px;font-size:12px}
.perms-page__empty-tag{color:#9ca3af;font-size:12px;font-style:italic}
.perms-page__pagination{display:flex;align-items:center;gap:12px;margin-top:16px;justify-content:center}
.perms-page__pagination button{padding:6px 14px;border:1px solid #d1d5db;border-radius:6px;background:#fff;cursor:pointer;font-size:13px;transition:all .2s}
.perms-page__pagination button:hover:not(:disabled){background:#f3f4f6}
.perms-page__pagination button:disabled{opacity:.4;cursor:not-allowed}
.perms-page__pagination span{font-size:13px;color:#6b7280}
.perms-page__overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:center;justify-content:center}
.perms-page__modal{background:#fff;border-radius:12px;padding:24px;width:420px;max-height:80vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.15)}
.perms-page__modal--wide{width:560px}
.perms-page__modal h3{font-size:18px;font-weight:600;margin-bottom:16px;color:#111827}
.perms-page__modal label{display:block;margin-bottom:12px;font-size:13px;font-weight:500;color:#374151}
.perms-page__modal input[type="text"],.perms-page__modal input:not([type]){width:100%;margin-top:4px;padding:8px 12px;border:1px solid #d1d5db;border-radius:6px;font-size:14px;outline:none;transition:border-color .2s}
.perms-page__modal input:focus{border-color:#4f46e5}
.perms-page__modal input:disabled{background:#f3f4f6;color:#6b7280}
.perms-page__modal-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:20px}
.perms-page__error{color:#dc2626;font-size:13px;margin-top:8px}
.perms-page__checkbox-list{max-height:240px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:6px;padding:8px;margin-top:4px}
.perms-page__checkbox{display:flex!important;align-items:flex-start;gap:8px;padding:6px 4px;border-radius:4px;cursor:pointer;font-weight:400!important}
.perms-page__checkbox:hover{background:#f9fafb}
.perms-page__checkbox input{margin-top:2px;accent-color:#4f46e5}
.perms-page__checkbox span{font-size:13px;color:#1f2937}
.perms-page__checkbox small{font-size:11px;color:#9ca3af;margin-left:auto}
</style>
