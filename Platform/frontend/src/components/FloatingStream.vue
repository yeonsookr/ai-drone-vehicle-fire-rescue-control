<script setup lang="ts">
import { ref, computed } from 'vue'
import { X, Plane, MapPin, Clock, CameraOff, Wifi, Maximize2, Minimize2 } from '@lucide/vue'
import { useTelemetryService } from '@/services/telemetryService'
import { useStreamService } from '@/services/streamService'

const props = defineProps<{ streamId: number; onGrab?: (e: PointerEvent) => void }>()
const emit = defineEmits<{ close: []; select: [id: number] }>()

const telemetry = useTelemetryService()
const streamSvc = useStreamService()
const expanded = ref(false)

const current = computed(() => streamSvc.ofId(props.streamId))

// Domain: drone is camera source, vehicle relays drone video to server
// Mock relay path: DRONE-001/002 → VEH-001, DRONE-003/004 → VEH-002
const relayVehicle = computed(() => {
  const id = current.value?.device_id
  if (!id) return null
  if (['DRONE-001', 'DRONE-002'].includes(id)) return 'VEH-001'
  if (['DRONE-003', 'DRONE-004'].includes(id)) return 'VEH-002'
  return null
})

const t = computed(() => {
  if (!current.value) return null
  return telemetry.latestOf(current.value.device_id) ?? null
})

const available = computed(() => streamSvc.active)
</script>

<template>
  <div :class="expanded ? 'w-240' : 'w-160'" class="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700 cursor-grab active:cursor-grabbing" @pointerdown="props.onGrab?.($event)">
      <div class="flex items-center gap-2">
        <Plane class="w-4 h-4 text-cyan-400" />
        <span class="text-sm font-semibold text-gray-100">{{ current?.device_id ?? 'Unknown' }}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">drone cam</span>
        <span v-if="current?.status === 'streaming'" class="text-[10px] text-green-400">LIVE</span>
      </div>
      <div class="flex items-center gap-1">
        <button @click="expanded = !expanded" @pointerdown.stop class="text-gray-500 hover:text-gray-300 p-1" :title="expanded ? 'Collapse' : 'Expand'">
          <Maximize2 v-if="!expanded" class="w-3.5 h-3.5" /><Minimize2 v-else class="w-3.5 h-3.5" />
        </button>
        <button @click="emit('close')" @pointerdown.stop class="text-gray-500 hover:text-gray-300 p-1"><X class="w-4 h-4" /></button>
      </div>
    </div>

    <!-- Video area -->
    <div class="relative bg-black" style="aspect-ratio: 16/9">
      <div v-if="!current || current.status !== 'streaming'" class="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-600 text-xs bg-gray-900">
        <CameraOff class="w-8 h-8" />
        <span>No video from {{ current?.device_id ?? 'drone' }}</span>
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
      <div class="absolute bottom-0 inset-x-0 bg-linear-to-t from-black/80 to-transparent px-3 py-2">
        <div class="flex items-center gap-4 text-[10px] text-gray-200">
          <span class="flex items-center gap-1"><MapPin class="w-3 h-3 text-gray-400" />{{ t ? `${t.latitude.toFixed(4)}, ${t.longitude.toFixed(4)}` : '--' }}</span>
          <span class="flex items-center gap-1"><Clock class="w-3 h-3 text-gray-400" />{{ t ? new Date(t.recorded_at).toLocaleTimeString() : '--' }}</span>
          <span v-if="t" class="text-gray-400">ALT {{ t.altitude.toFixed(0) }}m</span>
          <span class="ml-auto flex items-center gap-1 text-gray-500"><Wifi class="w-3 h-3" />{{ relayVehicle ?? '--' }}</span>
        </div>
      </div>
    </div>

    <!-- Camera switcher (drone cameras only) -->
    <div class="flex gap-1.5 px-3 py-2 border-t border-gray-700 overflow-x-auto">
      <button v-for="s in available" :key="s.id" @click="emit('select', s.id)"
        class="flex items-center gap-1 px-2 py-1 rounded text-[10px] transition-colors whitespace-nowrap"
        :class="s.id === props.streamId ? 'bg-gray-700 text-gray-100' : 'bg-gray-800 text-gray-500 hover:text-gray-300'"
      >
        <Plane class="w-3 h-3" />
        {{ s.device_id }}
      </button>
    </div>
  </div>
</template>
