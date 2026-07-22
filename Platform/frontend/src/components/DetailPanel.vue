<script setup lang="ts">
defineProps<{ title: string }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Transition name="slide">
    <div v-if="$slots.default" class="w-1/2 border-l border-gray-800 flex flex-col bg-gray-850">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800 shrink-0">
        <h3 class="text-sm font-semibold text-gray-100">{{ title }}</h3>
        <button @click="emit('close')" class="text-gray-500 hover:text-gray-300 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="flex-1 px-5 py-4 text-xs space-y-3 overflow-y-auto">
        <slot />
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: width 0.2s ease, opacity 0.2s ease; }
.slide-enter-from, .slide-leave-to { width: 0 !important; opacity: 0; overflow: hidden; }
</style>
