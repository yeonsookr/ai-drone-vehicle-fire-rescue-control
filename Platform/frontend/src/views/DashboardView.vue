<script setup lang="ts">
import { computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'

const telemetry = useTelemetryService()

const activeDrones = computed(() => telemetry.droneIds.length)
const streaming = computed(() => activeDrones.value)
</script>

<template>
  <div class="flex-1 flex gap-4 p-4 min-h-0">
    <div class="flex-1 flex flex-col gap-4 min-h-0">
      <div class="flex-1 bg-gray-800 rounded-lg border border-gray-700 p-2 flex flex-col">
        <div class="text-xs text-gray-400 mb-2 px-1">Camera Feed</div>
        <div class="flex-1 grid grid-cols-4 grid-rows-4 gap-1.5">
          <div v-for="i in 16" :key="i" class="bg-gray-900 rounded border border-gray-700 flex items-center justify-center text-xs text-gray-600 relative overflow-hidden" :class="{ 'ring-1 ring-gray-400': i === 1 }">
            <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 75"><line x1="0" y1="0" x2="100" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/><line x1="100" y1="0" x2="0" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/></svg>
            <span class="relative z-10">Cam {{ i }}</span>
          </div>
        </div>
      </div>
      <div class="h-14 bg-gray-800 rounded-lg border border-gray-700 flex items-center px-4 shrink-0">
        <span class="text-xs text-gray-500">Drones: {{ activeDrones }} | Gateways: {{ 1 }} | Streaming: {{ streaming }}</span>
      </div>
    </div>
  </div>
</template>
