<script setup lang="ts">
import { computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import Sidebar from '@/components/Sidebar.vue'
import DashboardBase from '@/components/DashboardBase.vue'

const telemetry = useTelemetryService()
const connected = computed(() => telemetry.connected)
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <Sidebar :connected="connected" />
    <main class="flex-1 flex min-h-0">
      <div class="w-1/2 flex flex-col min-h-0 border-r border-gray-800">
        <DashboardBase />
      </div>
      <router-view class="flex-1 flex flex-col min-h-0" />
    </main>
  </div>
</template>
