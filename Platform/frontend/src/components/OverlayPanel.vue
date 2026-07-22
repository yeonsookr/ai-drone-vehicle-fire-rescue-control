<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="h-full bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg flex flex-col overflow-hidden">
    <div class="h-12 flex items-center justify-between px-4 border-b border-gray-700 shrink-0">
      <h2 class="text-sm font-semibold text-gray-100">{{ title }}</h2>
      <slot name="badge" />
    </div>
    <div class="flex-1 overflow-y-auto p-3">
      <slot />
    </div>
  </div>
</template>
