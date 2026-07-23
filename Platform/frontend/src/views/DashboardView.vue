<script setup lang="ts">
import { ref, computed } from 'vue'
import { streamApi } from '@/lib/api/streams'
import { useUiStore } from '@/stores/ui'
import OverlayPanel from '@/components/OverlayPanel.vue'
import type { VideoStream } from '@/types'

const ui = useUiStore()
const streams = ref<VideoStream[]>([])
const droneStreams = computed(() => streams.value.filter(s => s.device_type === 'drone'))

streamApi.list().then(res => { streams.value = res.data })
</script>

<template>
  <div class="flex flex-col gap-4 h-full">
    <OverlayPanel>
      <div class="flex-1 grid grid-cols-2 auto-rows-min gap-2 content-start" style="min-height: 200px">
        <div
          v-for="s in droneStreams" :key="s.id"
          @click="ui.openStream(s.id)"
          class="aspect-video bg-gray-900/80 rounded border border-gray-700 flex items-center justify-center text-xs text-gray-600 relative overflow-hidden min-w-24 cursor-pointer transition-colors"
          :class="s.status === 'streaming' ? 'hover:border-gray-500 hover:bg-gray-900/60' : 'opacity-50'"
          :style="s.id === 1 ? 'border-color: rgb(156 163 175)' : ''"
        >
          <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 75"><line x1="0" y1="0" x2="100" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/><line x1="100" y1="0" x2="0" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/></svg>
          <span class="relative z-10">{{ s.device_id }}</span>
        </div>
      </div>
    </OverlayPanel>
  </div>
</template>
