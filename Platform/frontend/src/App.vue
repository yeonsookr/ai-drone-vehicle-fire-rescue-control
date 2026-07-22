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
    <Sidebar />
    <main class="flex-1 flex flex-col min-h-0">
      <!-- Full-width top header -->
      <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
        <h1 class="text-base font-bold text-gray-100">AIoT Dashboard</h1>
        <span
          class="text-xs px-2 py-0.5 rounded-full"
          :class="connected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'"
        >{{ connected ? '● Connected' : '○ Disconnected' }}</span>
      </header>
      <!-- Content row: left dashboard + right page -->
      <div class="flex-1 flex min-h-0">
        <div class="w-1/2 flex flex-col min-h-0 border-r border-gray-800">
          <DashboardBase />
        </div>
        <router-view class="flex-1 flex flex-col min-h-0" />
      </div>
    </main>
  </div>
</template>
