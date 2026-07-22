<script setup lang="ts">
import { onMounted } from 'vue'
import { useMissionService } from '@/services'
import { fmtTime } from '@/lib/format'
import {
  Plane, Satellite, Map as MapIcon,
  CircleCheck, CircleDot, X,
  Play, Pause, XCircle, AlertTriangle, List,
} from '@lucide/vue'

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

async function handleStart(id: string) {
  try { await ms.start(id) } catch { /* toast disabled */ }
}
async function handlePause(id: string) {
  try { await ms.pause(id) } catch { /* toast disabled */ }
}
async function handleResume(id: string) {
  try { await ms.resume(id) } catch { /* toast disabled */ }
}
async function handleCancel(id: string) {
  try { await ms.cancel(id) } catch { /* toast disabled */ }
}
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Missions</h1>
      <div class="flex items-center gap-2 text-xs text-gray-500">{{ ms.missions.length }} total</div>
    </header>
    <div class="flex-1 flex min-h-0">
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="ms.loading" class="text-xs text-gray-500">Loading...</div>
        <div v-else-if="ms.missions.length === 0" class="flex items-center justify-center h-full text-gray-500 text-xs">No missions.</div>
        <div v-else class="space-y-2">
          <div
            v-for="m in ms.missions" :key="m.id"
            @click="ms.select(m.id)"
            class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600"
            :class="{ 'border-gray-500': ms.selectedId === m.id }"
          >
            <MapIcon class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-gray-100">{{ m.id }}</span>
                <span class="text-xs text-gray-500">{{ m.type }}</span>
              </div>
              <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
                <span class="flex items-center gap-1"><Plane class="w-3 h-3" />{{ m.drone_id }}</span>
                <span class="flex items-center gap-1"><Satellite class="w-3 h-3" />{{ m.vehicle_id }}</span>
              </div>
            </div>
            <div class="text-right shrink-0">
              <div class="text-xs font-medium" :class="statusColor[m.status] || 'text-gray-400'">{{ m.status }}</div>
              <div class="text-[10px] text-gray-600 mt-0.5">{{ m.started_at ? fmtTime(m.started_at) : '-' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="ms.selected" class="w-1/2 border-l border-gray-800 flex flex-col bg-gray-850">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800 shrink-0">
          <h3 class="text-sm font-semibold text-gray-100">{{ ms.selected.id }}</h3>
          <button @click="ms.select(null)" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
        </div>

        <div class="flex-1 px-5 py-4 text-xs space-y-3 overflow-y-auto">
          <!-- 기본 정보 -->
          <div class="flex justify-between"><span class="text-gray-500">Type</span><span class="text-gray-200">{{ ms.selected.type }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor[ms.selected.status] || 'text-gray-400'">{{ ms.selected.status }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ ms.selected.drone_id }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Vehicle</span><span class="text-gray-200">{{ ms.selected.vehicle_id }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Created</span><span class="text-gray-200">{{ fmtTime(ms.selected.created_at) }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Started</span><span class="text-gray-200">{{ ms.selected.started_at ? fmtTime(ms.selected.started_at) : '-' }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Completed</span><span class="text-gray-200">{{ ms.selected.completed_at ? fmtTime(ms.selected.completed_at) : '-' }}</span></div>

          <!-- 생명주기 제어 버튼 -->
          <div class="flex items-center gap-2 pt-2 border-t border-gray-800">
            <button
              v-if="canStart(ms.selected)"
              @click="handleStart(ms.selected.id)"
              :disabled="ms.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-green-700 hover:bg-green-600 disabled:opacity-40 text-gray-100 rounded transition-colors"
            >
              <Play class="w-3.5 h-3.5" /> Start
            </button>
            <button
              v-if="canPause(ms.selected)"
              @click="handlePause(ms.selected.id)"
              :disabled="ms.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-orange-700 hover:bg-orange-600 disabled:opacity-40 text-gray-100 rounded transition-colors"
            >
              <Pause class="w-3.5 h-3.5" /> Pause
            </button>
            <button
              v-if="canResume(ms.selected)"
              @click="handleResume(ms.selected.id)"
              :disabled="ms.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-gray-100 rounded transition-colors"
            >
              <Play class="w-3.5 h-3.5" /> Resume
            </button>
            <button
              v-if="canCancel(ms.selected)"
              @click="handleCancel(ms.selected.id)"
              :disabled="ms.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-red-800 hover:bg-red-700 disabled:opacity-40 text-gray-100 rounded transition-colors"
            >
              <XCircle class="w-3.5 h-3.5" /> Cancel
            </button>
          </div>

          <!-- 실패 사유 -->
          <div
            v-if="ms.selected.status === 'FAILED' && ms.selected.failure_reason"
            class="flex items-start gap-2 bg-red-900/30 border border-red-800 rounded px-3 py-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <div>
              <div class="text-red-300 font-medium text-xs">Failure reason</div>
              <div class="text-red-200/80 text-[10px] mt-0.5">{{ ms.selected.failure_reason }}</div>
            </div>
          </div>

          <!-- 구간 ACK -->
          <div class="text-gray-500 text-xs pt-2 border-t border-gray-800">Section ACK</div>
          <div class="space-y-2">
            <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
              <CircleCheck v-if="ms.selected.status !== 'FAILED'" class="w-4 h-4 text-green-400 shrink-0" />
              <CircleDot v-else class="w-4 h-4 text-red-400 shrink-0" />
              <div class="flex-1"><div class="text-gray-200 font-medium">Server</div><div class="text-gray-500 text-[10px]">Command sent</div></div>
              <span class="text-[10px] font-mono" :class="segColor(ms.selected.status)">ACK</span>
            </div>
            <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
              <CircleCheck v-if="ms.selected.status !== 'FAILED'" class="w-4 h-4 text-green-400 shrink-0" />
              <CircleDot v-else class="w-4 h-4 text-red-400 shrink-0" />
              <div class="flex-1"><div class="text-gray-200 font-medium">{{ ms.selected.vehicle_id }}</div><div class="text-gray-500 text-[10px]">Relay via vehicle</div></div>
              <span class="text-[10px] font-mono" :class="segColor(ms.selected.status)">ACK</span>
            </div>
            <div class="flex items-center gap-3 bg-gray-900 rounded px-3 py-2">
              <CircleCheck v-if="ms.selected.status === 'COMPLETED'" class="w-4 h-4 text-green-400 shrink-0" />
              <CircleDot v-else class="w-4 h-4 text-gray-500 shrink-0" />
              <div class="flex-1"><div class="text-gray-200 font-medium">{{ ms.selected.drone_id }}</div><div class="text-gray-500 text-[10px]">Drone execution</div></div>
              <span class="text-[10px] font-mono" :class="segColor(ms.selected.status === 'COMPLETED' ? 'COMPLETED' : 'PENDING')">{{ ms.selected.status === 'COMPLETED' ? 'OK' : '...' }}</span>
            </div>
          </div>

          <!-- 명령 이력 -->
          <div class="text-gray-500 text-xs pt-2 border-t border-gray-800 flex items-center gap-1.5">
            <List class="w-3.5 h-3.5" /> Command History
          </div>
          <div v-if="ms.selectedCommands.length === 0" class="text-gray-600 text-[10px]">No commands recorded.</div>
          <div v-else class="space-y-1.5">
            <div
              v-for="cmd in ms.selectedCommands" :key="cmd.id"
              class="flex items-center gap-2 bg-gray-900 rounded px-3 py-2"
            >
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5">
                  <span class="text-gray-200 font-medium text-[10px]">{{ cmd.id }}</span>
                  <span class="text-[10px] px-1 rounded bg-gray-800 text-gray-400">{{ cmd.type }}</span>
                  <span :class="cmdStatusColor(cmd.status)" class="text-[10px]">{{ cmd.status }}</span>
                </div>
                <div class="text-gray-500 text-[10px] mt-0.5">
                  {{ cmd.target_id }} &middot; {{ fmtTime(cmd.issued_at) }}
                </div>
                <div v-if="cmd.status === 'FAILED' && cmd.error_reason" class="text-red-400 text-[10px] mt-0.5">
                  {{ cmd.error_reason }}
                </div>
              </div>
            </div>
          </div>

          <!-- 상태 전환 이력 -->
          <div class="text-gray-500 text-xs pt-2 border-t border-gray-800">Mission Log</div>
          <div v-if="ms.selectedLogs.length === 0" class="text-gray-600 text-[10px]">No logs recorded.</div>
          <div v-else class="space-y-1">
            <div
              v-for="log in ms.selectedLogs" :key="log.id"
              class="flex items-center gap-2 bg-gray-900 rounded px-3 py-1.5"
            >
              <span class="text-[10px] text-gray-500 shrink-0">{{ fmtTime(log.created_at) }}</span>
              <span :class="statusColor[log.status_from] || 'text-gray-400'" class="text-[10px]">{{ log.status_from }}</span>
              <span class="text-gray-600 text-[10px]">&rarr;</span>
              <span :class="statusColor[log.status_to] || 'text-gray-400'" class="text-[10px] font-medium">{{ log.status_to }}</span>
              <span v-if="log.reason" class="text-red-400/70 text-[10px] ml-1">({{ log.reason }})</span>
              <span class="text-gray-600 text-[10px] ml-auto">{{ log.changed_by }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
