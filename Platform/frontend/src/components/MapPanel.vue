<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '@/composables/useKakaoMap'
import { useTelemetryService } from '@/services/telemetryService'
import { Plus, Minus, Map as MapIcon, Satellite, Crosshair } from '@lucide/vue'

const telemetry = useTelemetryService()

const mapReady = ref(false)
const mapError = ref('')
const mapContainer = ref<HTMLElement | null>(null)
const mapType = ref(2)
const currentLevel = ref(8)

let kakaoMap: kakao.maps.Map | null = null
const markers = new Map<string, kakao.maps.Marker>()

function syncMarkers() {
  if (!kakaoMap || !mapReady.value) return
  const { makeMarker, moveMarker } = useKakaoMap()

  // Clean removed devices
  for (const [id, m] of markers) {
    if (!telemetry.droneIds.includes(id) && !telemetry.vehicleIds.includes(id)) {
      m.setMap(null); markers.delete(id)
    }
  }

  // Sync drone markers
  for (const id of telemetry.droneIds) {
    const t = telemetry.latestOf(id)
    if (!t) continue
    if (markers.has(id)) moveMarker(markers.get(id)!, t.latitude, t.longitude)
    else markers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
  }

  // Sync vehicle markers
  for (const id of telemetry.vehicleIds) {
    const t = telemetry.vehicleLatestOf(id)
    if (!t) continue
    if (markers.has(id)) moveMarker(markers.get(id)!, t.latitude, t.longitude)
    else markers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
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
  if (level > 1) { kakaoMap.setLevel(level - 1); currentLevel.value = level - 1 }
}

function zoomOut() {
  if (!kakaoMap) return
  const level = kakaoMap.getLevel()
  if (level < 13) { kakaoMap.setLevel(level + 1); currentLevel.value = level + 1 }
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

watch(() => telemetry.version, syncMarkers, { immediate: true })

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value, { lat: 37.5665, lng: 126.978 }, currentLevel.value)
      kakaoMap.setMapTypeId(mapType.value)
      currentLevel.value = kakaoMap.getLevel()
      mapReady.value = true
      syncMarkers()
    } catch (e: any) { mapError.value = e.message ?? 'Failed to load map' }
  }
  if (!telemetry.version) telemetry.start()
})

onUnmounted(() => {
  for (const m of markers.values()) m.setMap(null)
  markers.clear()
})
</script>

<template>
  <div ref="mapContainer" class="h-full w-full bg-gray-800 border-gray-700 relative overflow-hidden">
    <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm bg-gray-800/80 z-20">{{ mapError }}</div>
    <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-20">Loading map...</div>

    <!-- Map controls (bottom center) -->
    <div v-if="mapReady" class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex items-center gap-2 bg-gray-900/80 backdrop-blur rounded-lg border border-gray-700 px-2 py-1.5 shadow-lg">
      <button @click="toggleMapType" title="Map type" class="w-7 h-7 hover:bg-gray-700 rounded flex items-center justify-center text-xs text-gray-300 transition-colors">
        <MapIcon v-if="mapType === 1" class="w-3.5 h-3.5" /><Satellite v-else class="w-3.5 h-3.5" />
      </button>
      <div class="w-px h-5 bg-gray-700"></div>
      <button @click="goToCurrentLocation" title="My location" class="w-7 h-7 hover:bg-gray-700 rounded flex items-center justify-center text-xs text-gray-300 transition-colors">
        <Crosshair class="w-3.5 h-3.5" />
      </button>
      <div class="w-px h-5 bg-gray-700"></div>
      <button @click="zoomIn" title="Zoom in" class="w-7 h-7 hover:bg-gray-700 rounded flex items-center justify-center text-sm text-gray-200 transition-colors">
        <Plus class="w-3.5 h-3.5" />
      </button>
      <button @click="zoomOut" title="Zoom out" class="w-7 h-7 hover:bg-gray-700 rounded flex items-center justify-center text-sm text-gray-200 transition-colors">
        <Minus class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>
</template>
