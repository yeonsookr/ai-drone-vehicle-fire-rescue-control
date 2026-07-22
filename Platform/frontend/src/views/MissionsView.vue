<script setup lang="ts">
import { onMounted } from 'vue'
import { useMissionService } from '@/services'
import { fmtTime } from '@/lib/format'
import {
  Plane, Satellite, Map as MapIcon,
  CircleCheck, CircleDot, X,
  Play, Pause, XCircle, AlertTriangle, List,
} from '@lucide/vue'
import OverlayPanel from '@/components/OverlayPanel.vue'

const ms = useMissionService()

onMounted(() => ms.fetch())

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

async function handleStart(id: string) { try { await ms.start(id) } catch {} }
async function handlePause(id: string) { try { await ms.pause(id) } catch {} }
async function handleResume(id: string) { try { await ms.resume(id) } catch {} }
async function handleCancel(id: string) { try { await ms.cancel(id) } catch {} }
</script>

<template>
  <OverlayPanel title="Missions">
    <template #badge><span class="text-[10px] text-gray-500">{{ ms.missions.length }} total</span></template>

    <!-- Mission list -->
    <div v-if="ms.loading" class="text-xs text-gray-500">Loading...</div>
    <div v-else-if="ms.missions.length === 0" class="flex items-center justify-center h-20 text-gray-500 text-xs">No missions.</div>
    <div v-else class="space-y-2">
      <div
        v-for="m in ms.missions" :key="m.id"
        @click="ms.select(m.id)"
        class="flex items-center gap-3 px-3 py-2 bg-gray-900/80 rounded-lg border cursor-pointer transition-colors hover:border-gray-600"
        :class="ms.selectedId === m.id ? 'border-gray-500' : 'border-gray-700'"
      >
        <MapIcon class="w-4 h-4 text-gray-400 shrink-0" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-gray-100">{{ m.id }}</span>
            <span class="text-[10px] text-gray-500">{{ m.type }}</span>
          </div>
          <div class="flex items-center gap-2 mt-0.5 text-[10px] text-gray-500">
            <Plane class="w-2.5 h-2.5" />{{ m.drone_id }}
            <Satellite class="w-2.5 h-2.5 ml-1" />{{ m.vehicle_id }}
          </div>
        </div>
        <div class="text-right shrink-0">
          <div class="text-[11px] font-medium" :class="statusColor[m.status] || 'text-gray-400'">{{ m.status }}</div>
          <div class="text-[9px] text-gray-600 mt-0.5">{{ m.started_at ? fmtTime(m.started_at) : '-' }}</div>
        </div>
      </div>
    </div>

    <!-- Detail panel -->
    <div v-if="ms.selected" class="mt-3 border-t border-gray-700 pt-3 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-100">{{ ms.selected.id }}</h3>
        <button @click="ms.select(null)" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
      </div>

      <div class="flex justify-between text-[11px]"><span class="text-gray-500">Type</span><span class="text-gray-200">{{ ms.selected.type }}</span></div>
      <div class="flex justify-between text-[11px]"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor[ms.selected.status] || 'text-gray-400'">{{ ms.selected.status }}</span></div>
      <div class="flex justify-between text-[11px]"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ ms.selected.drone_id }}</span></div>
      <div class="flex justify-between text-[11px]"><span class="text-gray-500">Vehicle</span><span class="text-gray-200">{{ ms.selected.vehicle_id }}</span></div>

      <div class="flex items-center gap-2 pt-2 border-t border-gray-700">
        <button v-if="canStart(ms.selected)" @click="handleStart(ms.selected.id)" :disabled="ms.actionLoading" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-green-700 hover:bg-green-600 disabled:opacity-40 text-gray-100 rounded transition-colors"><Play class="w-3 h-3" /> Start</button>
        <button v-if="canPause(ms.selected)" @click="handlePause(ms.selected.id)" :disabled="ms.actionLoading" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-orange-700 hover:bg-orange-600 disabled:opacity-40 text-gray-100 rounded transition-colors"><Pause class="w-3 h-3" /> Pause</button>
        <button v-if="canResume(ms.selected)" @click="handleResume(ms.selected.id)" :disabled="ms.actionLoading" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-gray-100 rounded transition-colors"><Play class="w-3 h-3" /> Resume</button>
        <button v-if="canCancel(ms.selected)" @click="handleCancel(ms.selected.id)" :disabled="ms.actionLoading" class="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium bg-red-800 hover:bg-red-700 disabled:opacity-40 text-gray-100 rounded transition-colors"><XCircle class="w-3 h-3" /> Cancel</button>
      </div>

      <div v-if="ms.selected.status === 'FAILED' && ms.selected.failure_reason" class="flex items-start gap-2 bg-red-900/30 border border-red-800 rounded px-3 py-2">
        <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
        <div><div class="text-red-300 font-medium text-[11px]">Failure reason</div><div class="text-red-200/80 text-[10px] mt-0.5">{{ ms.selected.failure_reason }}</div></div>
      </div>

      <div class="text-gray-500 text-[11px] pt-2 border-t border-gray-700">Section ACK</div>
      <div class="space-y-1.5">
        <div class="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1.5">
          <CircleCheck v-if="ms.selected.status !== 'FAILED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-red-400 shrink-0" />
          <span class="flex-1 text-[11px] text-gray-200">Server</span>
          <span class="text-[10px] font-mono" :class="segColor(ms.selected.status)">ACK</span>
        </div>
        <div class="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1.5">
          <CircleCheck v-if="ms.selected.status !== 'FAILED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-red-400 shrink-0" />
          <span class="flex-1 text-[11px] text-gray-200">{{ ms.selected.vehicle_id }}</span>
          <span class="text-[10px] font-mono" :class="segColor(ms.selected.status)">ACK</span>
        </div>
        <div class="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1.5">
          <CircleCheck v-if="ms.selected.status === 'COMPLETED'" class="w-3.5 h-3.5 text-green-400 shrink-0" /><CircleDot v-else class="w-3.5 h-3.5 text-gray-500 shrink-0" />
          <span class="flex-1 text-[11px] text-gray-200">{{ ms.selected.drone_id }}</span>
          <span class="text-[10px] font-mono" :class="segColor(ms.selected.status === 'COMPLETED' ? 'COMPLETED' : 'PENDING')">{{ ms.selected.status === 'COMPLETED' ? 'OK' : '...' }}</span>
        </div>
      </div>

      <div class="text-gray-500 text-[11px] pt-2 border-t border-gray-700 flex items-center gap-1"><List class="w-3.5 h-3.5" /> Command History</div>
      <div v-if="ms.selectedCommands.length === 0" class="text-gray-600 text-[10px]">No commands recorded.</div>
      <div v-else class="space-y-1">
        <div v-for="cmd in ms.selectedCommands" :key="cmd.id" class="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1.5">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1">
              <span class="text-gray-200 font-medium text-[10px]">{{ cmd.id }}</span>
              <span class="text-[9px] px-1 rounded bg-gray-800 text-gray-400">{{ cmd.type }}</span>
              <span :class="cmdStatusColor(cmd.status)" class="text-[10px]">{{ cmd.status }}</span>
            </div>
            <div class="text-gray-500 text-[9px]">{{ cmd.target_id }} &middot; {{ fmtTime(cmd.issued_at) }}</div>
            <div v-if="cmd.status === 'FAILED' && cmd.error_reason" class="text-red-400 text-[9px]">{{ cmd.error_reason }}</div>
          </div>
        </div>
      </div>

      <div class="text-gray-500 text-[11px] pt-2 border-t border-gray-700">Mission Log</div>
      <div v-if="ms.selectedLogs.length === 0" class="text-gray-600 text-[10px]">No logs recorded.</div>
      <div v-else class="space-y-1">
        <div v-for="log in ms.selectedLogs" :key="log.id" class="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1">
          <span class="text-[9px] text-gray-500 shrink-0">{{ fmtTime(log.created_at) }}</span>
          <span :class="statusColor[log.status_from] || 'text-gray-400'" class="text-[9px]">{{ log.status_from }}</span>
          <span class="text-gray-600 text-[9px]">&rarr;</span>
          <span :class="statusColor[log.status_to] || 'text-gray-400'" class="text-[9px] font-medium">{{ log.status_to }}</span>
          <span v-if="log.reason" class="text-red-400/70 text-[9px]">({{ log.reason }})</span>
          <span class="text-gray-600 text-[9px] ml-auto">{{ log.changed_by }}</span>
        </div>
      </div>
    </div>
  </OverlayPanel>
</template>
