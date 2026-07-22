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
    <!-- Unified left panel: header + nav + page content -->
    <div class="w-80 flex flex-col min-h-0 bg-[#1a1a1a] border-r border-gray-800">
      <!-- Logo + status -->
      <div class="h-14 flex items-center justify-between px-4 border-b border-gray-800 shrink-0">
        <span class="text-[11px] font-bold tracking-widest text-gray-500 uppercase">AIoT CTRL</span>
        <span class="text-[10px]" :class="connected ? 'text-green-400' : 'text-red-400'">{{ connected ? '● Connected' : '○ Disconnected' }}</span>
      </div>
      <!-- Nav tabs -->
      <div class="shrink-0 border-b border-gray-800">
        <Sidebar />
      </div>
      <!-- Page content -->
      <div class="flex-1 flex flex-col min-h-0">
        <router-view class="flex-1 min-h-0" />
      </div>
    </div>
    <!-- Map full screen right -->
    <main class="flex-1 relative min-h-0">
      <MapPanel class="absolute inset-0" />
    </main>
  </div>
</template>
