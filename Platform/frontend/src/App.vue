<script setup lang="ts">
import { computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import { useUiStore } from '@/stores/ui'
import Sidebar from '@/components/Sidebar.vue'
import MapPanel from '@/components/MapPanel.vue'
import FloatingDetail from '@/components/FloatingDetail.vue'
import FloatingMissionDetail from '@/components/FloatingMissionDetail.vue'
import FloatingStream from '@/components/FloatingStream.vue'

const telemetry = useTelemetryService()
const ui = useUiStore()
const connected = computed(() => telemetry.connected)
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200" @click="ui.closeAll">
    <!-- Section 1: Sidebar + Content -->
    <div class="w-80 flex flex-col min-h-0 bg-[#1a1a1a] border-r border-gray-800" @click.stop>
      <div class="h-14 flex items-center justify-between px-4 border-b border-gray-800 shrink-0">
        <span class="text-[11px] font-bold tracking-widest text-gray-500 uppercase">AIoT CTRL</span>
        <span class="text-[10px]" :class="connected ? 'text-green-400' : 'text-red-400'">{{ connected ? '● Connected' : '○ Disconnected' }}</span>
      </div>
      <div class="shrink-0 border-b border-gray-800">
        <Sidebar />
      </div>
      <div class="flex-1 flex flex-col min-h-0">
        <router-view class="flex-1 min-h-0" />
      </div>
    </div>

    <!-- Map fills remaining area -->
    <main class="flex-1 relative min-h-0">
      <MapPanel class="absolute inset-0" />

      <!-- Section 2: Camera stream (centered, large) -->
      <div v-if="ui.streamId" class="absolute z-20 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" @click.stop>
        <FloatingStream
          :stream-id="ui.streamId"
          @close="ui.closeStream()"
          @select="ui.openStream"
        />
      </div>

      <!-- Section 3: Detail overlays (right side, overlap OK) -->
      <div v-if="ui.detailDeviceId" class="absolute z-30 top-4 right-4 h-11/12" @click.stop>
        <FloatingDetail :device-id="ui.detailDeviceId" @close="ui.closeDetail()" />
      </div>
      <div v-if="ui.missionId" class="absolute z-30 top-4 right-4 h-11/12" @click.stop>
        <FloatingMissionDetail :mission-id="ui.missionId" @close="ui.closeMission()" />
      </div>
    </main>
  </div>
</template>
