<script setup lang="ts">
import { onMounted } from 'vue'
import { useMissionService } from '@/services'
import { useUiStore } from '@/stores/ui'
import { fmtTime } from '@/lib/format'
import { MapIcon, Plane, Satellite } from '@lucide/vue'
import OverlayPanel from '@/components/OverlayPanel.vue'
import PanelSection from '@/components/PanelSection.vue'

const ui = useUiStore()
const ms = useMissionService()

onMounted(() => ms.fetch())

const statusColor: Record<string, string> = {
  CREATED: 'text-gray-400', ASSIGNED: 'text-cyan-400', DISPATCHED: 'text-blue-400',
  IN_PROGRESS: 'text-yellow-400', COMPLETED: 'text-green-400', PAUSED: 'text-orange-400',
  RETURNING: 'text-yellow-400', FAILED: 'text-red-400', CANCELLED: 'text-gray-500',
}
</script>

<template>
  <OverlayPanel>
    <PanelSection label="Missions">
      <template #badge><span class="text-[10px] text-gray-500">{{ ms.missions.length }} total</span></template>
    </PanelSection>

    <div v-if="ms.loading" class="text-xs text-gray-500">Loading...</div>
    <div v-else-if="ms.missions.length === 0" class="flex items-center justify-center h-20 text-gray-500 text-xs">No missions.</div>
    <div v-else class="space-y-2">
      <div
        v-for="m in ms.missions" :key="m.id"
        @click="ui.toggleMission(m.id)"
        class="flex items-center gap-3 px-3 py-2 bg-gray-900/80 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600"
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
  </OverlayPanel>
</template>
