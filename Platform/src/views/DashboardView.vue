<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '@/composables/useKakaoMap'
import { useTelemetryStore } from '@/stores/telemetry'
import type { DroneTelemetry } from '@/types'

const telemetry = useTelemetryStore()

const mapReady = ref(false)
const mapError = ref('')
const mapContainer = ref<HTMLElement | null>(null)

let kakaoMap: kakao.maps.Map | null = null
const markers = new Map<string, kakao.maps.Marker>()

function syncMarkers(map: Map<string, DroneTelemetry>) {
  if (!kakaoMap || !mapReady.value) return
  const { makeMarker, moveMarker } = useKakaoMap()

  for (const [id, t] of map) {
    if (markers.has(id)) {
      moveMarker(markers.get(id)!, t.latitude, t.longitude)
    } else {
      const m = makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id)
      markers.set(id, m)
    }
  }
}

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value)
      mapReady.value = true
    } catch (e: any) {
      mapError.value = e.message ?? 'Failed to load map'
    }
  }

  telemetry.start()
})

watch(() => telemetry.version, () => syncMarkers(telemetry.latest))

onUnmounted(() => {
  telemetry.stop()
  for (const m of markers.values()) m.setMap(null)
  markers.clear()
})
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Dashboard</h1>
      <span
        class="text-xs px-2.5 py-1 rounded-full"
        :class="telemetry.connected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'"
      >
        {{ telemetry.connected ? '● Connected' : '○ Disconnected' }}
      </span>
    </header>

    <div class="flex-1 p-4 min-h-0">
      <div ref="mapContainer" class="w-full h-full bg-gray-800 rounded-lg border border-gray-700 relative overflow-hidden">
        <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm bg-gray-800/80 z-10">
          {{ mapError }}
        </div>
        <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-10">
          Loading map...
        </div>
      </div>
    </div>
  </div>
</template>
