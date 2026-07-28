<template>
    <div class="user-card" :class="{ 'user-card--inactive': !user.is_active }">
        <div class="user-card__avatar">
            {{ initials }}
        </div>
        <div class="user-card__info">
            <div class="user-card__name">{{ user.first_name }} {{ user.last_name }}</div>
            <div class="user-card__email">{{ user.email }}</div>
            <div class="user-card__badges">
                <span v-if="user.is_superuser" class="badge badge--superuser">Admin</span>
                <span v-if="user.is_verified" class="badge badge--verified">Verified</span>
                <span v-if="user.is_banned" class="badge badge--banned">Banned</span>
                <span v-if="!user.is_active" class="badge badge--inactive">Inactive</span>
            </div>
        </div>
        <div class="user-card__actions">
            <button 
                v-if="user.is_active"
                class="btn btn--small btn--danger"
                @click="$emit('deactivate', user.id)"
            >
                Deactivate
            </button>
            <button class="btn btn--small" @click="$emit('edit', user)">
                Edit
            </button>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    user: {
        type: Object,
        required: true,
    },
})

defineEmits(['edit', 'deactivate'])

const initials = computed(() => {
    return `${props.user.first_name?.[0] || ''}${props.user.last_name?.[0] || ''}`.toUpperCase()
})
</script>

<style scoped>
.user-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s;
}

.user-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.user-card--inactive {
    opacity: 0.6;
}

.user-card__avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #4f46e5;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    flex-shrink: 0;
}

.user-card__info {
    flex: 1;
    min-width: 0;
}

.user-card__name {
    font-weight: 600;
    color: #1f2937;
}

.user-card__email {
    color: #6b7280;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-card__badges {
    display: flex;
    gap: 4px;
    margin-top: 4px;
    flex-wrap: wrap;
}

.badge {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
}

.badge--superuser {
    background: #fef3c7;
    color: #92400e;
}

.badge--verified {
    background: #d1fae5;
    color: #065f46;
}

.badge--banned {
    background: #fee2e2;
    color: #991b1b;
}

.badge--inactive {
    background: #f3f4f6;
    color: #6b7280;
}

.user-card__actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}

.btn {
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.2s;
}

.btn--small {
    padding: 4px 10px;
    font-size: 12px;
}

.btn--danger {
    background: #fee2e2;
    color: #991b1b;
}

.btn--danger:hover {
    background: #fecaca;
}

.btn--small:not(.btn--danger) {
    background: #e0e7ff;
    color: #3730a3;
}

.btn--small:not(.btn--danger):hover {
    background: #c7d2fe;
}
</style>
