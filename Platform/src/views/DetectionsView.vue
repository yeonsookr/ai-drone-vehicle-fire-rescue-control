<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Flame, Wind, Check, Ban, Clock } from '@lucide/vue'
import { useDetectionService } from '@/services/detectionService'
import type { OperatorJudgment } from '@/types'

const detection = useDetectionService()

const filter = ref<'all' | 'unconfirmed' | 'approved' | 'false_alarm'>('all')
const selectedId = ref<string | null>(null)

const filteredEvents = computed(() => {
  let data = detection.events
  if (filter.value === 'unconfirmed') data = data.filter((e: any) => e.operator_judgment === 'unconfirmed')
  else if (filter.value === 'approved') data = data.filter((e: any) => e.operator_judgment === 'approved')
  else if (filter.value === 'false_alarm') data = data.filter((e: any) => e.operator_judgment === 'false_alarm')
  return data
})

const selectedEvent = computed(() => {
  if (!selectedId.value) return null
  return detection.events.find((e: any) => e.id === selectedId.value) ?? null
})

function typeIcon(t: string) { return t === 'forest_fire' ? Flame : Wind }
function typeLabel(t: string) { return { forest_fire: 'Forest Fire', smoke: 'Smoke' }[t] ?? t }
function typeColor(t: string) { return { forest_fire: 'text-red-400', smoke: 'text-yellow-400' }[t] ?? 'text-gray-400' }
function statusColor(s: string) { return { unconfirmed: 'text-yellow-400', approved: 'text-green-400', false_alarm: 'text-gray-500', pending: 'text-blue-400' }[s] ?? 'text-gray-400' }

function select(id: string) { selectedId.value = selectedId.value === id ? null : id }
async function handleJudge(judgment: OperatorJudgment) { if (selectedId.value) await detection.judge(selectedId.value, judgment) }

onMounted(() => { detection.fetch() })
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Detections</h1>
      <span class="text-xs px-2.5 py-1 rounded-full bg-yellow-900 text-yellow-300">{{ detection.alertCount }} pending</span>
    </header>
    <div class="flex items-center gap-2 px-6 py-2.5 border-b border-gray-800 shrink-0">
      <button v-for="f in [{ key: 'all', label: 'All' }, { key: 'unconfirmed', label: 'Unconfirmed' }, { key: 'approved', label: 'Approved' }, { key: 'false_alarm', label: 'False Alarm' }]" :key="f.key" @click="filter = f.key as any; selectedId = null" class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors" :class="filter === f.key ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'">{{ f.label }}</button>
    </div>
    <div class="flex-1 flex min-h-0">
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="filteredEvents.length === 0" class="flex items-center justify-center h-full text-gray-500 text-xs">No detections found.</div>
        <div class="space-y-2">
          <div v-for="e in filteredEvents" :key="e.id" @click="select(e.id)" class="flex items-center gap-3 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600" :class="{ 'border-gray-500': selectedId === e.id }">
            <component :is="typeIcon(e.detection_type)" class="w-5 h-5 shrink-0" :class="typeColor(e.detection_type)" />
            <div class="flex-1 min-w-0"><div class="flex items-center gap-2"><span class="text-sm font-semibold text-gray-100">{{ e.id }}</span><span class="text-xs" :class="typeColor(e.detection_type)">{{ typeLabel(e.detection_type) }}</span></div><div class="flex items-center gap-3 mt-0.5 text-xs text-gray-500"><span>{{ (e.confidence * 100).toFixed(0) }}% confidence</span><span>{{ e.latitude.toFixed(4) }}, {{ e.longitude.toFixed(4) }}</span></div></div>
            <div class="text-right shrink-0"><div class="text-xs font-medium" :class="statusColor(e.operator_judgment)">{{ e.operator_judgment }}</div><div class="text-[10px] text-gray-600 mt-0.5">{{ e.detected_at.slice(11, 19) }}</div></div>
          </div>
        </div>
      </div>
      <div class="w-96 border-l border-gray-800 overflow-y-auto shrink-0 p-4">
        <div v-if="!selectedEvent" class="flex items-center justify-center h-full text-gray-600 text-xs">Select an event</div>
        <template v-if="selectedEvent">
          <div class="space-y-4">
            <div><div class="flex items-center gap-2 mb-3"><component :is="typeIcon(selectedEvent.detection_type)" class="w-5 h-5" :class="typeColor(selectedEvent.detection_type)" /><div><div class="text-sm font-semibold text-gray-100">{{ selectedEvent.id }}</div><div class="text-xs text-gray-500">{{ typeLabel(selectedEvent.detection_type) }}</div></div></div>
              <div class="w-full h-44 bg-gray-900 rounded-lg border border-gray-700 flex items-center justify-center text-gray-600 text-xs mb-3 relative overflow-hidden">
                <span>Snapshot</span>
                <div class="absolute border-2 border-red-500/60 rounded" :style="{ left: selectedEvent.bounding_box.x / 4 + 'px', top: selectedEvent.bounding_box.y / 4 + 'px', width: selectedEvent.bounding_box.w / 4 + 'px', height: selectedEvent.bounding_box.h / 4 + 'px' }">
                  <span class="absolute -top-4 left-0 text-[10px] text-red-400 whitespace-nowrap">{{ typeLabel(selectedEvent.detection_type) }} {{ (selectedEvent.confidence * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
            <div class="text-xs space-y-2">
              <div class="flex justify-between"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ selectedEvent.drone_id ?? '-' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Confidence</span><span class="text-gray-200">{{ (selectedEvent.confidence * 100).toFixed(0) }}%</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Location</span><span class="text-gray-200 font-mono">{{ selectedEvent.latitude.toFixed(4) }}, {{ selectedEvent.longitude.toFixed(4) }}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Source</span><span class="text-gray-200">{{ selectedEvent.source }}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor(selectedEvent.operator_judgment)">{{ selectedEvent.operator_judgment }}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Detected</span><span class="text-gray-200">{{ selectedEvent.detected_at.slice(0, 19) }}</span></div>
            </div>
            <div v-if="selectedEvent.operator_judgment === 'unconfirmed'" class="flex gap-2 pt-2 border-t border-gray-800">
              <button @click="handleJudge('approved')" class="flex-1 flex items-center justify-center gap-1.5 py-2 bg-green-800 hover:bg-green-700 rounded-lg text-xs text-green-200 transition-colors"><Check class="w-3.5 h-3.5" /> Approve</button>
              <button @click="handleJudge('false_alarm')" class="flex-1 flex items-center justify-center gap-1.5 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs text-gray-300 transition-colors"><Ban class="w-3.5 h-3.5" /> False Alarm</button>
              <button @click="handleJudge('pending')" class="flex-1 flex items-center justify-center gap-1.5 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs text-gray-300 transition-colors"><Clock class="w-3.5 h-3.5" /> Pending</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
