<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTelemetryService } from '@/services/telemetryService'
import Sidebar from '@/components/Sidebar.vue'
import MapPanel from '@/components/MapPanel.vue'
import FloatingDetail from '@/components/FloatingDetail.vue'

const route = useRoute()
const router = useRouter()
const telemetry = useTelemetryService()
const connected = computed(() => telemetry.connected)

const detailId = computed(() => route.query.detail as string | undefined)

// Close detail on escape key
watch(() => detailId.value, () => {})

function closeDetail() {
  router.replace({ query: { ...route.query, detail: undefined } })
}
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <!-- Left panel -->
    <div class="w-80 flex flex-col min-h-0 bg-[#1a1a1a] border-r border-gray-800">
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

    <!-- Map full screen -->
    <main class="flex-1 relative min-h-0" @click="closeDetail">
      <MapPanel class="absolute inset-0" />
    </main>

    <!-- Floating detail overlay on map -->
    <div
      v-if="detailId"
      class="absolute z-20 top-4 right-4"
      @click.stop
    >
      <FloatingDetail :device-id="detailId" @close="closeDetail" />
    </div>
  </div>
</template>
