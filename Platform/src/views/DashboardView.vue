<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '@/composables/useKakaoMap'
import { useTelemetryStore } from '@/stores/telemetry'
import type { DroneTelemetry } from '@/types'
import { Plus, Minus, Map as MapIcon, Satellite, Crosshair } from '@lucide/vue'

const telemetry = useTelemetryStore()

const mapReady = ref(false)
const mapError = ref('')
const mapContainer = ref<HTMLElement | null>(null)
const mapType = ref(2) // 1=ROADMAP, 2=SKYVIEW
const currentLevel = ref(8)

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

function toggleMapType() {
  if (!kakaoMap) return
  const next = mapType.value === 1 ? 2 : 1
  kakaoMap.setMapTypeId(next)
  mapType.value = next
}

function zoomIn() {
  if (!kakaoMap) return
  const level = kakaoMap.getLevel()
  if (level > 1) {
    kakaoMap.setLevel(level - 1)
    currentLevel.value = level - 1
  }
}

function zoomOut() {
  if (!kakaoMap) return
  const level = kakaoMap.getLevel()
  if (level < 13) {
    kakaoMap.setLevel(level + 1)
    currentLevel.value = level + 1
  }
}

function goToCurrentLocation() {
  if (!navigator.geolocation || !kakaoMap) return
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const latlng = new window.kakao.maps.LatLng(pos.coords.latitude, pos.coords.longitude)
      kakaoMap!.setCenter(latlng)
      kakaoMap!.setLevel(5)
      currentLevel.value = 5
    },
    () => {},
    { enableHighAccuracy: true, timeout: 5000 },
  )
}

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value, { lat: 37.5665, lng: 126.978 }, currentLevel.value)
      kakaoMap.setMapTypeId(mapType.value)
      currentLevel.value = kakaoMap.getLevel()
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

    <section class="flex-1 flex gap-4 p-4 min-h-0">
      <!-- Left: Map (50%) -->
      <div ref="mapContainer" class="flex-1 bg-gray-800 rounded-lg border border-gray-700 relative overflow-hidden">
        <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm bg-gray-800/80 z-20">
          {{ mapError }}
        </div>
        <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-20">
          Loading map...
        </div>

        <!-- Map controls (top-right) -->
        <div v-if="mapReady" class="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
          <button
            @click="toggleMapType"
            title="Map type"
            class="w-9 h-9 bg-gray-900/80 hover:bg-gray-900 rounded-lg border border-gray-600 flex items-center justify-center text-xs text-gray-300 transition-colors"
          >
            <MapIcon v-if="mapType === 1" class="w-4 h-4" />
            <Satellite v-else class="w-4 h-4" />
          </button>
          <button
            @click="goToCurrentLocation"
            title="My location"
            class="w-9 h-9 bg-gray-900/80 hover:bg-gray-900 rounded-lg border border-gray-600 flex items-center justify-center text-xs text-gray-300 transition-colors"
          >
            <Crosshair class="w-4 h-4" />
          </button>
        </div>

        <!-- Zoom controls (bottom-right) -->
        <div v-if="mapReady" class="absolute bottom-3 right-3 z-10 flex flex-col gap-px rounded-lg overflow-hidden shadow-lg">
          <button
            @click="zoomIn"
            title="Zoom in"
            class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors border-b border-gray-700"
          >
            <Plus class="w-4 h-4" />
          </button>
          <button
            @click="zoomOut"
            title="Zoom out"
            class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors"
          >
            <Minus class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Right: placeholder (50%) -->
      <div class="flex-1 flex flex-col gap-4 min-h-0">
        <div class="flex-1 bg-gray-800 rounded-lg border border-gray-700 flex items-center justify-center text-gray-600 text-sm">
          Camera grid (next)
        </div>
        <div class="h-16 bg-gray-800 rounded-lg border border-gray-700 flex items-center px-4 text-gray-600 text-sm">
          Status bar (next)
        </div>
      </div>
    </section>
  </div>
</template>
