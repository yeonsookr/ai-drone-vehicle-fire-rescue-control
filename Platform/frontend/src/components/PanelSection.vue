<script setup lang="ts">
defineProps<{ label: string }>()
</script>

<template>
  <div class="flex items-center justify-between mb-3">
    <span class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">{{ label }}</span>
    <slot name="badge" />
  </div>
</template>
