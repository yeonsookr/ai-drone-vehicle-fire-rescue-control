<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '@/composables/useKakaoMap'
import { useTelemetryService } from '@/services/telemetryService'
import { useDeviceService } from '@/services/deviceService'
import { Plane, Satellite, Camera, TriangleAlert } from '@lucide/vue'

const props = defineProps<{ mini?: boolean }>()

const telemetry = useTelemetryService()
const device = useDeviceService()

const mapReady = ref(false)
const mapError = ref('')
const mapContainer = ref<HTMLElement | null>(null)
const currentLevel = ref(8)

let kakaoMap: kakao.maps.Map | null = null
const markers = new Map<string, kakao.maps.Marker>()

const activeDrones = computed(() => telemetry.droneIds.length)
const activeVehicles = computed(() => telemetry.vehicleIds.length)
const activeGateways = computed(() => telemetry.connected ? 1 : 0)
const connected = computed(() => telemetry.connected)

function syncMarkers() {
  if (!kakaoMap || !mapReady.value) return
  const { makeMarker, moveMarker } = useKakaoMap()

  // Clean removed
  for (const [id, m] of markers) {
    if (!telemetry.droneIds.includes(id) && !telemetry.vehicleIds.includes(id)) {
      m.setMap(null); markers.delete(id)
    }
  }

  for (const id of telemetry.droneIds) {
    const t = telemetry.latestOf(id)
    if (!t) continue
    if (markers.has(id)) moveMarker(markers.get(id)!, t.latitude, t.longitude)
    else markers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
  }
  for (const id of telemetry.vehicleIds) {
    const t = telemetry.vehicleLatestOf(id)
    if (!t) continue
    if (markers.has(id)) moveMarker(markers.get(id)!, t.latitude, t.longitude)
    else markers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
  }
}

watch(() => telemetry.version, syncMarkers)

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      const center = { lat: 37.5665, lng: 126.978 }
      const level = props.mini ? 10 : 8
      kakaoMap = await createMap(mapContainer.value, center, level)
      mapReady.value = true
      currentLevel.value = level
    } catch (e: any) { mapError.value = e.message ?? 'Map load failed' }
  }
  if (!telemetry.version) telemetry.start()
})

onUnmounted(() => {
  for (const m of markers.values()) m.setMap(null)
  markers.clear()
})
</script>

<template>
  <div
    class="border-b border-gray-800 transition-all duration-300 overflow-hidden"
    :class="mini ? 'h-40 shrink-0' : 'flex-1 flex flex-col min-h-0'"
  >
    <!-- Status bar -->
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Dashboard</h1>
      <div class="flex items-center gap-3">
        <span class="text-xs px-2 py-0.5 rounded-full" :class="connected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'">{{ connected ? '● Connected' : '○ Disconnected' }}</span>
        <span v-if="device.disconnectedDevices.length > 0" class="text-xs px-2 py-0.5 rounded-full bg-red-900 text-red-300">! {{ device.disconnectedDevices.length }} disconnected</span>
      </div>
    </header>
    <!-- Stats bar -->
    <section class="h-12 flex items-center gap-4 px-6 border-b border-gray-800 shrink-0" v-if="!mini">
      <div class="flex items-center gap-2 flex-1 h-8 bg-gray-800 rounded-lg px-3">
        <Plane class="w-4 h-4 text-gray-400 shrink-0" />
        <span class="text-xs text-gray-500">Drones</span>
        <span class="text-sm font-bold text-gray-100 ml-auto">{{ activeDrones }}</span>
      </div>
      <div class="flex items-center gap-2 flex-1 h-8 bg-gray-800 rounded-lg px-3">
        <Satellite class="w-4 h-4 text-gray-400 shrink-0" />
        <span class="text-xs text-gray-500">Vehicles</span>
        <span class="text-sm font-bold text-gray-100 ml-auto">{{ activeVehicles }}</span>
      </div>
      <div class="flex items-center gap-2 flex-1 h-8 bg-gray-800 rounded-lg px-3">
        <Camera class="w-4 h-4 text-gray-400 shrink-0" />
        <span class="text-xs text-gray-500">Gateways</span>
        <span class="text-sm font-bold text-gray-100 ml-auto">{{ activeGateways }}</span>
      </div>
      <div class="flex items-center gap-2 flex-1 h-8 bg-gray-800 rounded-lg px-3">
        <TriangleAlert class="w-4 h-4 text-gray-400 shrink-0" />
        <span class="text-xs text-gray-500">Alerts</span>
        <span class="text-sm font-bold text-gray-100 ml-auto">{{ device.disconnectedDevices.length }}</span>
      </div>
    </section>
    <!-- Map -->
    <div
      ref="mapContainer"
      class="bg-gray-800 border-gray-700 relative overflow-hidden"
      :class="mini ? 'h-28' : 'flex-1 border-b'"
    >
      <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm bg-gray-800/80 z-20">{{ mapError }}</div>
      <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-20">Loading map...</div>
    </div>
  </div>
</template>
