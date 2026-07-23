<script setup lang="ts">
import { computed } from 'vue'
import { X, Plane, Satellite, MapPin, Clock, CameraOff } from '@lucide/vue'
import { useTelemetryService } from '@/services/telemetryService'
import { streamApi } from '@/lib/api/streams'
import type { VideoStream } from '@/types'

const props = defineProps<{ streamId: number }>()
const emit = defineEmits<{ close: []; select: [id: number] }>()

const telemetry = useTelemetryService()

const streams = ref<VideoStream[]>([])
streamApi.list().then(res => { streams.value = res.data })

import { ref } from 'vue'

const current = computed(() => streams.value.find(s => s.id === props.streamId) ?? null)

const t = computed(() => {
  if (!current.value) return null
  const id = current.value.device_id
  return telemetry.latestOf(id) ?? telemetry.vehicleLatestOf(id) ?? null
})

const available = computed(() => streams.value.filter(s => s.status === 'streaming'))
</script>

<template>
  <div class="w-[560px] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700">
      <div class="flex items-center gap-2">
        <component :is="current?.device_type === 'drone' ? Plane : Satellite" v-if="current" class="w-4 h-4" :class="current?.device_type === 'drone' ? 'text-cyan-400' : 'text-yellow-400'" />
        <span class="text-sm font-semibold text-gray-100">{{ current?.device_id ?? 'Unknown' }}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">{{ current?.device_type }}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded" :class="current?.status === 'streaming' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'">{{ current?.status }}</span>
      </div>
      <button @click="emit('close')" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
    </div>

    <div class="relative bg-black" style="aspect-ratio: 16/9">
      <div v-if="!current || current.status !== 'streaming'" class="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-600 text-xs bg-gray-900">
        <CameraOff class="w-8 h-8" />
        <span>Stream offline</span>
      </div>
      <div v-else class="absolute inset-0 bg-gray-900 flex items-center justify-center">
        <svg class="w-full h-full opacity-5" viewBox="0 0 200 120">
          <line x1="0" y1="0" x2="200" y2="120" stroke="currentColor" stroke-width="0.5"/>
          <line x1="200" y1="0" x2="0" y2="120" stroke="currentColor" stroke-width="0.5"/>
        </svg>
        <span class="absolute text-gray-600 text-xs">Live feed — {{ current.device_id }}</span>
      </div>

      <!-- AI mock overlay -->
      <div v-if="current?.status === 'streaming'" class="absolute top-1/3 left-1/3 border-2 border-red-500/80 rounded" style="width: 140px; height: 90px">
        <span class="absolute -top-4 left-0 text-[9px] bg-red-500/80 text-white px-1 rounded-t">Fire 0.87</span>
      </div>

      <!-- Info bar -->
      <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent px-3 py-2">
        <div class="flex items-center gap-4 text-[10px] text-gray-200">
          <span class="flex items-center gap-1"><MapPin class="w-3 h-3 text-gray-400" />{{ t ? `${t.latitude.toFixed(4)}, ${t.longitude.toFixed(4)}` : '--' }}</span>
          <span class="flex items-center gap-1"><Clock class="w-3 h-3 text-gray-400" />{{ t ? new Date(t.recorded_at).toLocaleTimeString() : '--' }}</span>
          <span v-if="t" class="text-gray-400">ALT {{ t.altitude.toFixed(0) }}m</span>
        </div>
      </div>
    </div>

    <div class="flex gap-1.5 px-3 py-2 border-t border-gray-700 overflow-x-auto">
      <button v-for="s in available" :key="s.id" @click="emit('select', s.id)"
        class="flex items-center gap-1 px-2 py-1 rounded text-[10px] transition-colors whitespace-nowrap"
        :class="s.id === props.streamId ? 'bg-gray-700 text-gray-100' : 'bg-gray-800 text-gray-500 hover:text-gray-300'"
      >
        <component :is="s.device_type === 'drone' ? Plane : Satellite" class="w-3 h-3" />
        {{ s.device_id }}
      </button>
    </div>
  </div>
</template>
