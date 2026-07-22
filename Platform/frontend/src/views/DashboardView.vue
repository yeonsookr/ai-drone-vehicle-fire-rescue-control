<script setup lang="ts">
import OverlayPanel from '@/components/OverlayPanel.vue'
</script>

<template>
  <div class="flex flex-col gap-4 h-full">
    <OverlayPanel>
      <div class="flex-1 grid grid-cols-2 auto-rows-min gap-2 content-start" style="min-height: 200px">
        <div v-for="i in 4" :key="i" class="aspect-video bg-gray-900/80 rounded border border-gray-700 flex items-center justify-center text-xs text-gray-600 relative overflow-hidden min-w-24" :class="{ 'ring-1 ring-gray-400': i === 1 }">
          <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 75"><line x1="0" y1="0" x2="100" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/><line x1="100" y1="0" x2="0" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/></svg>
          <span class="relative z-10">Cam {{ i }}</span>
        </div>
      </div>
    </OverlayPanel>
  </div>
</template>
