<script setup lang="ts">
import { computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import Sidebar from '@/components/Sidebar.vue'
import MapPanel from '@/components/MapPanel.vue'

const telemetry = useTelemetryService()
const connected = computed(() => telemetry.connected)
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <Sidebar :connected="connected" />
    <main class="flex-1 relative min-h-0">
      <MapPanel class="absolute inset-0 z-0" />
      <div class="absolute top-4 right-4 bottom-4 z-10 flex pointer-events-none">
        <div class="w-80 flex flex-col pointer-events-auto min-h-0">
          <router-view class="flex-1 min-h-0" />
        </div>
      </div>
    </main>
  </div>
</template>
