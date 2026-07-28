<template>
    <div class="pagination" v-if="totalPages > 1">
        <button
            class="pagination__btn"
            :disabled="currentPage === 1"
            @click="$emit('page-change', currentPage - 1)"
        >
            ← Prev
        </button>
        
        <span class="pagination__info">
            Page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <button
            class="pagination__btn"
            :disabled="currentPage >= totalPages"
            @click="$emit('page-change', currentPage + 1)"
        >
            Next →
        </button>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    currentPage: { type: Number, required: true },
    totalItems: { type: Number, required: true },
    perPage: { type: Number, required: true },
})

defineEmits(['page-change'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.perPage))
</script>

<style scoped>
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 24px;
}

.pagination__btn {
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.pagination__btn:hover:not(:disabled) {
    background: #f3f4f6;
}

.pagination__btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.pagination__info {
    font-size: 14px;
    color: #6b7280;
}
</style>
