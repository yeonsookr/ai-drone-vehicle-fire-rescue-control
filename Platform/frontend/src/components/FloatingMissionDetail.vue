<script setup lang="ts">
import { computed, ref } from 'vue'
import { X, Play, Pause, XCircle, AlertTriangle, CircleCheck, CircleDot } from '@lucide/vue'
import { useMissionService } from '@/services'
import { fmtTime } from '@/lib/format'

const props = defineProps<{ missionId: string }>()
const emit = defineEmits<{ close: [] }>()

const ms = useMissionService()

const mission = computed(() => ms.missions.find(m => m.id === props.missionId) ?? null)
const commands = computed(() => ms.selectedCommands)
const logs = computed(() => ms.selectedLogs)
const activeTab = ref<'info' | 'commands' | 'log'>('info')

// Load data when opened
ms.select(props.missionId)

const statusColor: Record<string, string> = {
  CREATED: 'text-gray-400', ASSIGNED: 'text-cyan-400', DISPATCHED: 'text-blue-400',
  IN_PROGRESS: 'text-yellow-400', COMPLETED: 'text-green-400', PAUSED: 'text-orange-400',
  RETURNING: 'text-yellow-400', FAILED: 'text-red-400', CANCELLED: 'text-gray-500',
}

function segColor(s: string) {
  return s === 'COMPLETED' ? 'text-green-400' : s === 'FAILED' ? 'text-red-400' : 'text-gray-500'
}

function cmdStatusColor(s: string) {
  return s === 'SUCCEEDED' ? 'text-green-400' : s === 'FAILED' ? 'text-red-400' : s === 'RUNNING' ? 'text-blue-400' : 'text-gray-500'
}

function canStart(m: { status: string }) { return m.status === 'CREATED' }
function canPause(m: { status: string }) { return m.status === 'IN_PROGRESS' }
function canResume(m: { status: string }) { return m.status === 'PAUSED' }
function canCancel(m: { status: string }) { return ['CREATED', 'IN_PROGRESS', 'PAUSED'].includes(m.status) }
</script>

<template>
  <div class="w-96 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden max-h-[80vh]">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-gray-100">{{ props.missionId }}</span>
        <span v-if="mission" class="text-[10px] px-1.5 py-0.5 rounded" :class="mission.status === 'FAILED' ? 'bg-red-900 text-red-300' : 'bg-gray-800 text-gray-400'">{{ mission.status }}</span>
      </div>
      <button @click="emit('close')" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-0 border-b border-gray-700">
      <button @click="activeTab = 'info'" class="flex-1 py-2 text-[10px] font-medium transition-colors" :class="activeTab === 'info' ? 'text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-300'">Info</button>
      <button @click="activeTab = 'commands'" class="flex-1 py-2 text-[10px] font-medium transition-colors" :class="activeTab === 'commands' ? 'text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-300'">Commands</button>
      <button @click="activeTab = 'log'" class="flex-1 py-2 text-[10px] font-medium transition-colors" :class="activeTab === 'log' ? 'text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-300'">Log</button>
    </div>

    <div class="flex-1 overflow-y-auto p-3 text-xs min-h-0">
      <template v-if="activeTab === 'info' && mission">
        <div class="space-y-2 mb-3">
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Type</span><span class="text-gray-200">{{ mission.type }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor[mission.status] || ''">{{ mission.status }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ mission.drone_id }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Vehicle</span><span class="text-gray-200">{{ mission.vehicle_id }}</span></div>
        </div>

        <div class="flex items-center gap-2 pt-2 border-t border-gray-700 mb-3" v-if="canStart(mission) || canPause(mission) || canResume(mission) || canCancel(mission)">
          <button v-if="canStart(mission)" @click="ms.start(mission.id)" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-green-700 hover:bg-green-600 disabled:opacity-40 text-gray-100 rounded"><Play class="w-3 h-3" /> Start</button>
          <button v-if="canPause(mission)" @click="ms.pause(mission.id)" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-orange-700 hover:bg-orange-600 disabled:opacity-40 text-gray-100 rounded"><Pause class="w-3 h-3" /> Pause</button>
          <button v-if="canResume(mission)" @click="ms.resume(mission.id)" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-gray-100 rounded"><Play class="w-3 h-3" /> Resume</button>
          <button v-if="canCancel(mission)" @click="ms.cancel(mission.id)" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-red-800 hover:bg-red-700 disabled:opacity-40 text-gray-100 rounded"><XCircle class="w-3 h-3" /> Cancel</button>
        </div>

        <div v-if="mission.status === 'FAILED' && mission.failure_reason" class="flex items-start gap-2 bg-red-900/30 border border-red-800 rounded px-3 py-2 mb-3">
          <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div class="text-red-300 font-medium text-[11px]">Failure reason</div>
            <div class="text-red-200/80 text-[10px] mt-0.5">{{ mission.failure_reason }}</div>
          </div>
        </div>

        <div class="text-gray-500 text-[11px] mb-2">Section ACK</div>
        <div class="space-y-1.5">
          <div class="flex items-center gap-2 bg-gray-800/60 rounded px-2 py-1.5">
            <CircleCheck v-if="mission.status !== 'FAILED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-red-400 shrink-0" />
            <span class="flex-1 text-[11px] text-gray-200">Server</span>
            <span class="text-[10px] font-mono" :class="segColor(mission.status)">ACK</span>
          </div>
          <div class="flex items-center gap-2 bg-gray-800/60 rounded px-2 py-1.5">
            <CircleCheck v-if="mission.status !== 'FAILED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-red-400 shrink-0" />
            <span class="flex-1 text-[11px] text-gray-200">{{ mission.vehicle_id }}</span>
            <span class="text-[10px] font-mono" :class="segColor(mission.status)">ACK</span>
          </div>
          <div class="flex items-center gap-2 bg-gray-800/60 rounded px-2 py-1.5">
            <CircleCheck v-if="mission.status === 'COMPLETED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-gray-500 shrink-0" />
            <span class="flex-1 text-[11px] text-gray-200">{{ mission.drone_id }}</span>
            <span class="text-[10px] font-mono" :class="segColor(mission.status === 'COMPLETED' ? 'COMPLETED' : 'PENDING')">{{ mission.status === 'COMPLETED' ? 'OK' : '...' }}</span>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'commands'">
        <div v-if="commands.length === 0" class="text-gray-600 text-[10px] text-center py-8">No commands recorded.</div>
        <div v-else class="space-y-1">
          <div v-for="cmd in commands" :key="cmd.id" class="flex items-center gap-2 bg-gray-800/60 rounded px-2 py-1.5">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1">
                <span class="text-gray-200 font-medium text-[10px]">{{ cmd.id }}</span>
                <span class="text-[9px] px-1 rounded bg-gray-800 text-gray-400">{{ cmd.type }}</span>
                <span :class="cmdStatusColor(cmd.status)" class="text-[10px]">{{ cmd.status }}</span>
              </div>
              <div class="text-gray-500 text-[9px]">{{ cmd.target_id }} · {{ fmtTime(cmd.issued_at) }}</div>
              <div v-if="cmd.status === 'FAILED' && cmd.error_reason" class="text-red-400 text-[9px]">{{ cmd.error_reason }}</div>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'log'">
        <div v-if="logs.length === 0" class="text-gray-600 text-[10px] text-center py-8">No logs recorded.</div>
        <div v-else class="space-y-1">
          <div v-for="log in logs" :key="log.id" class="flex items-center gap-2 bg-gray-800/60 rounded px-2 py-1">
            <span class="text-[9px] text-gray-500 shrink-0">{{ fmtTime(log.created_at) }}</span>
            <span :class="statusColor[log.status_from] || 'text-gray-400'" class="text-[9px]">{{ log.status_from }}</span>
            <span class="text-gray-600 text-[9px]">→</span>
            <span :class="statusColor[log.status_to] || 'text-gray-400'" class="text-[9px] font-medium">{{ log.status_to }}</span>
            <span v-if="log.reason" class="text-red-400/70 text-[9px]">({{ log.reason }})</span>
            <span class="text-gray-600 text-[9px] ml-auto">{{ log.changed_by }}</span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
