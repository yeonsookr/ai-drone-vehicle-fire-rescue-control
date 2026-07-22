<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '@/composables/useKakaoMap'
import { useTelemetryService } from '@/services/telemetryService'
import { useDeviceService } from '@/services/deviceService'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js'
import {
  Plane, Map as MapIcon, Satellite,
  Plus, Minus, Wifi, WifiOff, X,
} from '@lucide/vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const telemetry = useTelemetryService()
const device = useDeviceService()

// ── UI-only state ──
const mapReady = ref(false)
const mapError = ref('')
const mapContainer = ref<HTMLElement | null>(null)
const mapType = ref(2)
const currentLevel = ref(8)
const selectedDevice = ref<string | null>(null)

let kakaoMap: kakao.maps.Map | null = null
const droneMarkers = new Map<string, kakao.maps.Marker>()
const vehicleMarkers = new Map<string, kakao.maps.Marker>()

// ── Device selection & chart data ──
const selectedHistory = computed(() => {
  if (!selectedDevice.value) return []
  return device.deviceHistoryOf(selectedDevice.value).slice(-60)
})

const chartOptions = {
  responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
  scales: { x: { display: false }, y: { display: true, ticks: { color: '#6b7280', font: { size: 9 }, maxTicksLimit: 4 }, grid: { color: '#374151' }, beginAtZero: true } },
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
}

function makeChartData(values: number[], color: string, fillColor: string) {
  return { labels: values.map(() => ''), datasets: [{ data: values, borderColor: color, backgroundColor: fillColor, borderWidth: 1.5, pointRadius: 0, fill: true, tension: 0.3 }] }
}

// Split chart line into segments based on signal threshold to highlight disconnected sections
function makeGapChartData(items: any[], field: string, color: string, fillColor: string, signalColor: string) {
  const labels: string[] = []
  const values: number[] = []
  const backgrounds: string[] = []  // pointBackgroundColor per point
  for (let i = 0; i < items.length; i++) {
    labels.push('')
    values.push(items[i][field])
    backgrounds.push((items[i].signal_strength as number) < -85 ? signalColor : color)
  }
  return {
    labels,
    datasets: [{
      data: values,
      borderColor: color,
      backgroundColor: fillColor,
      borderWidth: 1.5,
      pointRadius: 0,
      fill: true,
      tension: 0.3,
      segment: {
        borderColor: (ctx: any) => {
          const sig = (items[ctx.p1DataIndex] as any)?.signal_strength ?? -60
          return sig < -85 ? signalColor : color
        },
      },
    }],
  }
}

const chartData = computed(() => {
  const h = selectedHistory.value
  if (h.length === 0) return null

  return {
    altitude: makeGapChartData(h, 'altitude', '#22d3ee', 'rgba(34,211,238,0.08)', '#ef4444'),
    speed: makeGapChartData(h, 'speed', '#34d399', 'rgba(52,211,153,0.08)', '#ef4444'),
    battery: makeGapChartData(h, 'battery_level', '#fbbf24', 'rgba(251,191,36,0.08)', '#ef4444'),
    signal: makeChartData(h.map((t: any) => t.signal_strength), '#f472b6', 'rgba(244,114,182,0.08)'),
  }
})

const gapRanges = computed(() => {
  const h = selectedHistory.value as any[]
  const ranges: Array<{ from: number; to: number }> = []
  let start = -1
  for (let i = 0; i < h.length; i++) {
    if (h[i].signal_strength < -85) {
      if (start === -1) start = i
    } else {
      if (start !== -1) { ranges.push({ from: start, to: i }); start = -1 }
    }
  }
  if (start !== -1) ranges.push({ from: start, to: h.length })
  return ranges
})

// ── Format helpers ──
function batteryColor(b: number) { return b > 60 ? 'text-green-400' : b > 30 ? 'text-yellow-400' : 'text-red-400' }
function signalColor(s: number) { return s > -75 ? 'text-green-400' : s > -85 ? 'text-yellow-400' : 'text-red-400' }

// ── Map ──
function syncMarkers() {
  if (!kakaoMap || !mapReady.value) return
  const { makeMarker, moveMarker } = useKakaoMap()

  const currentDrones = new Set(telemetry.droneIds)
  for (const [id, m] of droneMarkers) { if (!currentDrones.has(id)) { m.setMap(null); droneMarkers.delete(id) } }
  for (const id of telemetry.droneIds) {
    const t = telemetry.latestOf(id)
    if (!t) continue
    if (droneMarkers.has(id)) moveMarker(droneMarkers.get(id)!, t.latitude, t.longitude)
    else droneMarkers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
  }

  const currentVehicles = new Set(telemetry.vehicleIds)
  for (const [id, m] of vehicleMarkers) { if (!currentVehicles.has(id)) { m.setMap(null); vehicleMarkers.delete(id) } }
  for (const id of telemetry.vehicleIds) {
    const t = telemetry.vehicleLatestOf(id)
    if (!t) continue
    if (vehicleMarkers.has(id)) moveMarker(vehicleMarkers.get(id)!, t.latitude, t.longitude)
    else vehicleMarkers.set(id, makeMarker(kakaoMap, { lat: t.latitude, lng: t.longitude }, id))
  }
}

watch(() => telemetry.version, syncMarkers)

function toggleMapType() {
  if (!kakaoMap) return
  const next = mapType.value === 1 ? 2 : 1
  kakaoMap.setMapTypeId(next)
  mapType.value = next
}

function zoomIn() {
  if (!kakaoMap) return
  const lvl = Math.max(1, kakaoMap.getLevel() - 1)
  kakaoMap.setLevel(lvl); currentLevel.value = lvl
}
function zoomOut() {
  if (!kakaoMap) return
  const lvl = Math.min(13, kakaoMap.getLevel() + 1)
  kakaoMap.setLevel(lvl); currentLevel.value = lvl
}

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value, { lat: 37.5665, lng: 126.978 }, currentLevel.value)
      kakaoMap.setMapTypeId(mapType.value)
      currentLevel.value = kakaoMap.getLevel()
      mapReady.value = true
    } catch (e: any) { mapError.value = e.message ?? 'Map load failed' }
  }
  telemetry.start()
})

onUnmounted(() => {
  telemetry.stop()
  for (const m of droneMarkers.values()) m.setMap(null)
  for (const m of vehicleMarkers.values()) m.setMap(null)
  droneMarkers.clear(); vehicleMarkers.clear()
})
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <header class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Telemetry</h1>
      <div class="flex items-center gap-3">
        <span class="text-xs px-2 py-0.5 rounded-full" :class="telemetry.connected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'">{{ telemetry.connected ? '● Connected' : '○ Disconnected' }}</span>
        <span v-if="device.disconnectedDevices.length > 0" class="text-xs px-2 py-0.5 rounded-full bg-red-900 text-red-300">! {{ device.disconnectedDevices.length }} disconnected</span>
      </div>
    </header>

    <div class="flex-1 flex gap-4 p-4 min-h-0">
      <!-- Map -->
      <div ref="mapContainer" class="flex-1 bg-gray-800 rounded-lg border border-gray-700 relative overflow-hidden">
        <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm bg-gray-800/80 z-20">{{ mapError }}</div>
        <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-20">Loading map...</div>
        <div v-if="mapReady" class="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
          <button @click="toggleMapType" class="w-9 h-9 bg-gray-900/80 hover:bg-gray-900 rounded-lg border border-gray-600 flex items-center justify-center text-xs text-gray-300 transition-colors">
            <MapIcon v-if="mapType === 1" class="w-4 h-4" /><Satellite v-else class="w-4 h-4" />
          </button>
        </div>
        <div v-if="mapReady" class="absolute bottom-3 right-3 z-10 flex flex-col gap-px rounded-lg overflow-hidden shadow-lg">
          <button @click="zoomIn" class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors border-b border-gray-700"><Plus class="w-4 h-4" /></button>
          <button @click="zoomOut" class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors"><Minus class="w-4 h-4" /></button>
        </div>
      </div>

      <!-- Right Panel: Cards + Charts -->
      <div class="flex-1 flex flex-col gap-4 min-h-0">
        <!-- Equipment Cards -->
        <div class="flex-1 bg-gray-800 rounded-lg border border-gray-700 p-3 flex flex-col min-h-0">
          <div class="text-xs text-gray-400 mb-2 shrink-0">Devices <span class="text-gray-600">({{ telemetry.droneIds.length + telemetry.vehicleIds.length }})</span></div>
          <div v-if="device.equipmentCards.length === 0" class="flex items-center justify-center flex-1 text-gray-600 text-xs">Waiting for telemetry...</div>
          <div v-else class="flex-1 overflow-y-auto grid grid-cols-2 gap-2 auto-rows-max content-start">
            <div
              v-for="card in device.equipmentCards" :key="card.id"
              @click="selectedDevice = selectedDevice === card.id ? null : card.id"
              class="bg-gray-900 rounded-lg border px-3 py-2 cursor-pointer transition-colors hover:border-gray-600"
              :class="[selectedDevice === card.id ? 'border-gray-500' : 'border-gray-700', card.stale ? 'opacity-50' : '']"
            >
              <div class="flex items-center gap-2 mb-1.5">
                <Plane v-if="card.type === 'drone'" class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-cyan-400'" />
                <Satellite v-else class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-yellow-400'" />
                <span class="text-xs font-medium text-gray-200 truncate flex-1">{{ card.id }}</span>
                <Wifi v-if="!card.stale && card.signal >= -85" class="w-3 h-3 text-green-400 shrink-0" />
                <WifiOff v-else class="w-3 h-3 text-red-400 shrink-0" />
              </div>
              <div class="grid grid-cols-2 gap-x-3 gap-y-1 text-[10px]">
                <div class="flex justify-between"><span class="text-gray-500">Bat</span><span class="font-medium" :class="batteryColor(card.battery)">{{ card.battery.toFixed(0) }}%</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Alt</span><span class="text-gray-300">{{ card.altitude.toFixed(0) }}m</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Spd</span><span class="text-gray-300">{{ card.speed.toFixed(1) }}m/s</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Sig</span><span class="font-medium" :class="signalColor(card.signal)">{{ card.signal.toFixed(0) }}dBm</span></div>
              </div>
              <div v-if="card.stale" class="mt-1 text-[9px] text-red-400/80">No data > 4s</div>
              <div v-else-if="card.signal < -85" class="mt-1 text-[9px] text-yellow-400/80">Weak signal</div>
            </div>
          </div>
        </div>

        <!-- Disconnected Summary + Charts -->
        <div v-if="selectedDevice" class="shrink-0 bg-gray-800 rounded-lg border border-gray-700 p-3 flex flex-col" style="height: 260px">
          <div class="flex items-center justify-between mb-2 shrink-0">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-200">{{ selectedDevice }}</span>
              <span class="text-[10px] text-gray-500">{{ selectedHistory.length }} pts</span>
              <span v-if="gapRanges.length > 0" class="text-[10px] text-red-400">{{ gapRanges.length }} gap(s)</span>
            </div>
            <button @click="selectedDevice = null" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
          </div>
          <div v-if="!chartData || selectedHistory.length < 2" class="flex items-center justify-center flex-1 text-gray-600 text-xs">Collecting data...</div>
          <div v-else class="flex-1 grid grid-cols-2 grid-rows-2 gap-2 min-h-0">
            <div v-for="item in [{ t: 'Alt', d: chartData.altitude, c: '#22d3ee' }, { t: 'Speed', d: chartData.speed, c: '#34d399' }, { t: 'Battery', d: chartData.battery, c: '#fbbf24' }, { t: 'Signal', d: chartData.signal, c: '#f472b6' }]" :key="item.t" class="bg-gray-900 rounded p-1.5 flex flex-col">
              <div class="text-[10px] text-gray-500 mb-0.5">{{ item.t }}</div>
              <div class="flex-1 min-h-0">
                <Line :data="item.d" :options="chartOptions" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
