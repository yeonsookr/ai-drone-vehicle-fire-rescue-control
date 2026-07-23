<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import { streamApi } from '@/lib/api/streams'
import OverlayPanel from '@/components/OverlayPanel.vue'
import PanelSection from '@/components/PanelSection.vue'
import { Plane, Satellite, MapPin, Clock, Camera } from '@lucide/vue'
import type { VideoStream } from '@/types'

const telemetry = useTelemetryService()

const streams = ref<VideoStream[]>([])
const selectedId = ref<number | null>(null)

streamApi.list().then(res => { streams.value = res.data })

const selectedStream = computed(() => streams.value.find(s => s.id === selectedId.value) ?? null)

function telemetryOf(deviceId: string) {
  const t = telemetry.latestOf(deviceId)
  if (t) return t
  return telemetry.vehicleLatestOf(deviceId)
}

const streamTelemetry = computed(() => {
  if (!selectedStream.value) return null
  return telemetryOf(selectedStream.value.device_id)
})

const filteredStreams = computed(() => streams.value.filter(s => s.status === 'streaming'))
</script>

<template>
  <OverlayPanel>
    <PanelSection label="Video Streams">
      <template #badge><span class="text-[10px] text-gray-500">{{ filteredStreams.length }} live</span></template>
    </PanelSection>

    <!-- Stream list -->
    <div v-if="streams.length === 0" class="text-gray-600 text-xs text-center py-8">No streams available.</div>
    <div v-else class="space-y-2 mb-4">
      <div
        v-for="s in streams" :key="s.id"
        @click="selectedId = selectedId === s.id ? null : s.id"
        class="flex items-center gap-3 px-3 py-2 bg-gray-900/80 rounded-lg border cursor-pointer transition-colors hover:border-gray-600"
        :class="[selectedId === s.id ? 'border-gray-500' : 'border-gray-700', s.status === 'inactive' ? 'opacity-50' : '']"
      >
        <Camera class="w-4 h-4" :class="s.status === 'streaming' ? 'text-green-400' : 'text-gray-500'" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-gray-100">{{ s.device_id }}</span>
            <span class="text-[10px] px-1 rounded bg-gray-800 text-gray-400">{{ s.device_type }}</span>
          </div>
          <div class="text-[10px] text-gray-500">{{ s.status }}</div>
        </div>
      </div>
    </div>

    <!-- Video player / placeholder -->
    <div v-if="!selectedStream" class="flex items-center justify-center h-40 text-gray-600 text-xs border border-dashed border-gray-700 rounded-lg">
      Select a camera to view feed
    </div>
    <div v-else class="relative bg-black rounded-lg overflow-hidden border border-gray-700" style="aspect-ratio: 16/9">
      <!-- Placeholder video feed -->
      <div class="absolute inset-0 bg-gray-900 flex items-center justify-center">
        <svg class="w-full h-full opacity-10" viewBox="0 0 200 120">
          <line x1="0" y1="0" x2="200" y2="120" stroke="currentColor" stroke-width="0.5" class="text-gray-400"/>
          <line x1="200" y1="0" x2="0" y2="120" stroke="currentColor" stroke-width="0.5" class="text-gray-400"/>
          <rect x="50" y="30" width="100" height="60" stroke="currentColor" stroke-width="0.5" fill="none" class="text-gray-400"/>
        </svg>
        <span class="absolute text-gray-600 text-xs">Live feed placeholder</span>
      </div>

      <!-- AI detection mock overlay -->
      <div class="absolute top-1/4 left-1/4 border-2 border-red-500/80 rounded" style="width: 120px; height: 80px">
        <span class="absolute -top-4 left-0 text-[9px] bg-red-500/80 text-white px-1 rounded-t">Fire 0.87</span>
      </div>

      <!-- Info overlay (bottom) -->
      <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent px-3 py-2">
        <div class="flex items-center gap-4 text-[10px] text-gray-200">
          <span class="flex items-center gap-1">
            <Plane v-if="selectedStream.device_type === 'drone'" class="w-3 h-3 text-cyan-400" />
            <Satellite v-else class="w-3 h-3 text-yellow-400" />
            {{ selectedStream.device_id }}
          </span>
          <span class="flex items-center gap-1 text-gray-400">
            <MapPin class="w-3 h-3" />
            {{ streamTelemetry ? `${streamTelemetry.latitude.toFixed(4)}, ${streamTelemetry.longitude.toFixed(4)}` : '--' }}
          </span>
          <span class="flex items-center gap-1 text-gray-400">
            <Clock class="w-3 h-3" />
            {{ streamTelemetry?.recorded_at ? new Date(streamTelemetry.recorded_at).toLocaleTimeString() : '--' }}
          </span>
        </div>
      </div>
    </div>
  </OverlayPanel>
</template>
