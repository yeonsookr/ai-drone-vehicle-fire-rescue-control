<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="h-12 flex items-center justify-between px-4 border-b border-gray-800 shrink-0">
      <h2 class="text-sm font-semibold text-gray-100">{{ title }}</h2>
      <slot name="badge" />
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <slot />
    </div>
  </div>
</template>
