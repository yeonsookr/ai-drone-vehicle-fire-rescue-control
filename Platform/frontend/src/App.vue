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
      <!-- Map fills entire main area -->
      <MapPanel class="absolute inset-0 z-0" />
      <!-- Page overlays on top of map -->
      <div class="absolute inset-0 z-10 flex justify-end p-4 pointer-events-none">
        <div class="w-1/2 flex flex-col pointer-events-auto">
          <router-view />
        </div>
      </div>
    </main>
  </div>
</template>
