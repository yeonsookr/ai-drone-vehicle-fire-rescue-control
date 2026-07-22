<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { missionApi } from '@/lib/api/missions'
import { fmtTime } from '@/lib/format'
import { Plane, Satellite, Map as MapIcon, CircleCheck, CircleDot, X } from '@lucide/vue'

const missions = ref<any[]>([])
const loading = ref(false)
const selectedId = ref<string | null>(null)

const selected = computed(() => {
  if (!selectedId.value) return null
  return missions.value.find(m => m.id === selectedId.value) ?? null
})

function statusColor(s: string) {
  return { CREATED: 'text-gray-400', ASSIGNED: 'text-cyan-400', DISPATCHED: 'text-blue-400', IN_PROGRESS: 'text-yellow-400', COMPLETED: 'text-green-400', PAUSED: 'text-orange-400', RETURNING: 'text-yellow-400', FAILED: 'text-red-400', CANCELLED: 'text-gray-500' }[s] ?? 'text-gray-400'
}
function segmentStatus(s: string) {
  return s === 'COMPLETED' ? 'text-green-400' : s === 'FAILED' ? 'text-red-400' : 'text-gray-500'
}
function select(id: string) { selectedId.value = selectedId.value === id ? null : id }

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await missionApi.list()
    missions.value = data
  } finally { loading.value = false }
})
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Missions</h1>
      <div class="flex items-center gap-2 text-xs text-gray-500">{{ missions.length }} total</div>
    </header>
    <div class="flex-1 flex min-h-0">
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="loading" class="text-xs text-gray-500">Loading...</div>
        <div v-else-if="missions.length === 0" class="flex items-center justify-center h-full text-gray-500 text-xs">No missions.</div>
        <div v-else class="space-y-2">
          <div v-for="m in missions" :key="m.id" @click="select(m.id)" class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600" :class="{ 'border-gray-500': selectedId === m.id }">
            <MapIcon class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2"><span class="text-sm font-semibold text-gray-100">{{ m.id }}</span><span class="text-xs text-gray-500">{{ m.type }}</span></div>
              <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
                <span class="flex items-center gap-1"><Plane class="w-3 h-3" />{{ m.drone_id }}</span>
                <span class="flex items-center gap-1"><Satellite class="w-3 h-3" />{{ m.vehicle_id }}</span>
              </div>
            </div>
            <div class="text-right shrink-0">
              <div class="text-xs font-medium" :class="statusColor(m.status)">{{ m.status }}</div>
              <div class="text-[10px] text-gray-600 mt-0.5">{{ m.started_at ? fmtTime(m.started_at) : '-' }}</div>
            </div>
          </div>
        </div>
      </div>
      <Transition name="slide">
        <div v-if="selected" class="w-96 border-l border-gray-800 flex flex-col bg-gray-850">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800 shrink-0">
            <h3 class="text-sm font-semibold text-gray-100">{{ selected.id }}</h3>
            <button @click="selectedId = null" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
          </div>
          <div class="flex-1 px-5 py-4 text-xs space-y-3 overflow-y-auto">
            <div class="flex justify-between"><span class="text-gray-500">Type</span><span class="text-gray-200">{{ selected.type }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor(selected.status)">{{ selected.status }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ selected.drone_id }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Vehicle</span><span class="text-gray-200">{{ selected.vehicle_id }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Created</span><span class="text-gray-200">{{ fmtTime(selected.created_at) }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Started</span><span class="text-gray-200">{{ selected.started_at ? fmtTime(selected.started_at) : '-' }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Completed</span><span class="text-gray-200">{{ selected.completed_at ? fmtTime(selected.completed_at) : '-' }}</span></div>
            <div class="text-gray-500 text-xs pt-2 border-t border-gray-800">Section ACK</div>
            <div class="space-y-2">
              <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
                <CircleCheck v-if="selected.status !== 'FAILED'" class="w-4 h-4 text-green-400 shrink-0" />
                <CircleDot v-else class="w-4 h-4 text-red-400 shrink-0" />
                <div class="flex-1"><div class="text-gray-200 font-medium">Server</div><div class="text-gray-500 text-[10px]">Command sent</div></div>
                <span class="text-[10px] font-mono" :class="segmentStatus(selected.status)">ACK</span>
              </div>
              <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
                <CircleCheck v-if="selected.status !== 'FAILED'" class="w-4 h-4 text-green-400 shrink-0" />
                <CircleDot v-else class="w-4 h-4 text-red-400 shrink-0" />
                <div class="flex-1"><div class="text-gray-200 font-medium">{{ selected.vehicle_id }}</div><div class="text-gray-500 text-[10px]">Relay via vehicle</div></div>
                <span class="text-[10px] font-mono" :class="segmentStatus(selected.status)">ACK</span>
              </div>
              <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
                <CircleCheck v-if="selected.status === 'COMPLETED'" class="w-4 h-4 text-green-400 shrink-0" />
                <CircleDot v-else class="w-4 h-4 text-gray-500 shrink-0" />
                <div class="flex-1"><div class="text-gray-200 font-medium">{{ selected.drone_id }}</div><div class="text-gray-500 text-[10px]">Drone execution</div></div>
                <span class="text-[10px] font-mono" :class="segmentStatus(selected.status === 'COMPLETED' ? 'COMPLETED' : 'PENDING')">{{ selected.status === 'COMPLETED' ? 'OK' : '...' }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: width 0.2s ease, opacity 0.2s ease; }
.slide-enter-from, .slide-leave-to { width: 0 !important; opacity: 0; overflow: hidden; }
</style>
