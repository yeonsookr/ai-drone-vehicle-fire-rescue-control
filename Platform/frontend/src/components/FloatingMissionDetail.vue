<script setup lang="ts">
import { computed } from 'vue'
import { X, AlertTriangle } from '@lucide/vue'
import { useMissionService } from '@/services'

const props = defineProps<{ missionId: string; onGrab?: (e: PointerEvent) => void }>()
const emit = defineEmits<{ close: [] }>()

const ms = useMissionService()
const mission = computed(() => ms.missions.find(m => m.id === props.missionId) ?? null)

ms.select(props.missionId)
</script>

<template>
  <div class="w-96 h-full bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700 cursor-grab active:cursor-grabbing" @pointerdown="props.onGrab?.($event)">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-gray-100">{{ props.missionId }}</span>
        <span v-if="mission" class="text-[10px] px-1.5 py-0.5 rounded" :class="mission.status === 'FAILED' ? 'bg-red-900 text-red-300' : 'bg-gray-800 text-gray-400'">{{ mission.status }}</span>
      </div>
      <button @click="emit('close')" @pointerdown.stop class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
    </div>

    <div class="flex-1 overflow-y-auto p-3 text-xs min-h-75">
      <template v-if="mission">
        <div class="space-y-2 mb-3">
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Type</span><span class="text-gray-200">{{ mission.type }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Status</span><span class="text-gray-200">{{ mission.status }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Drone</span><span class="text-gray-200">{{ mission.drone_id }}</span></div>
          <div class="flex justify-between text-[11px]"><span class="text-gray-500">Vehicle</span><span class="text-gray-200">{{ mission.vehicle_id }}</span></div>
        </div>

        <div v-if="mission.status === 'FAILED' && mission.failure_reason" class="flex items-start gap-2 bg-red-900/30 border border-red-800 rounded px-3 py-2">
          <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div class="text-red-300 font-medium text-[11px]">Failure reason</div>
            <div class="text-red-200/80 text-[10px] mt-0.5">{{ mission.failure_reason }}</div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
