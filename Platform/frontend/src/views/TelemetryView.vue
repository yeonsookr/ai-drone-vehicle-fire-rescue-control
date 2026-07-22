<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDeviceService } from '@/services/deviceService'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js'
import { Plane, Satellite, Wifi, WifiOff, X } from '@lucide/vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const device = useDeviceService()

const selectedDevice = ref<string | null>(null)

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

function makeGapChartData(items: any[], field: string, color: string, fillColor: string) {
  return {
    labels: items.map(() => ''),
    datasets: [{
      data: items.map((t: any) => t[field]),
      borderColor: color, backgroundColor: fillColor,
      borderWidth: 1.5, pointRadius: 0, fill: true, tension: 0.3,
      segment: { borderColor: (ctx: any) => (items[ctx.p1DataIndex] as any)?.signal_strength < -85 ? '#ef4444' : color },
    }],
  }
}

const chartData = computed(() => {
  const h = selectedHistory.value
  if (h.length < 2) return null
  return {
    altitude: makeGapChartData(h, 'altitude', '#22d3ee', 'rgba(34,211,238,0.08)'),
    speed: makeGapChartData(h, 'speed', '#34d399', 'rgba(52,211,153,0.08)'),
    battery: makeGapChartData(h, 'battery_level', '#fbbf24', 'rgba(251,191,36,0.08)'),
    signal: makeChartData(h.map((t: any) => t.signal_strength), '#f472b6', 'rgba(244,114,182,0.08)'),
  }
})

function batteryColor(b: number) { return b > 60 ? 'text-green-400' : b > 30 ? 'text-yellow-400' : 'text-red-400' }
function signalColor(s: number) { return s > -75 ? 'text-green-400' : s > -85 ? 'text-yellow-400' : 'text-red-400' }
</script>

<template>
  <div class="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg flex flex-col min-h-0 overflow-hidden">
    <div class="h-12 flex items-center justify-between px-4 border-b border-gray-700 shrink-0">
      <h2 class="text-sm font-semibold text-gray-100">Telemetry</h2>
      <span v-if="device.disconnectedDevices.length > 0" class="text-[10px] px-2 py-0.5 rounded-full bg-red-900 text-red-300">! {{ device.disconnectedDevices.length }} disconnected</span>
    </div>
    <div class="flex-1 overflow-y-auto p-3 space-y-3">
      <div v-if="device.equipmentCards.length === 0" class="flex items-center justify-center h-20 text-gray-600 text-xs">Waiting for telemetry...</div>
      <div v-else class="grid grid-cols-2 gap-2">
        <div v-for="card in device.equipmentCards" :key="card.id" @click="selectedDevice = selectedDevice === card.id ? null : card.id"
          class="bg-gray-900/80 rounded-lg border px-3 py-2 cursor-pointer transition-colors hover:border-gray-600"
          :class="[selectedDevice === card.id ? 'border-gray-500' : 'border-gray-700', card.stale ? 'opacity-50' : '']">
          <div class="flex items-center gap-2 mb-1.5">
            <Plane v-if="card.type === 'drone'" class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-cyan-400'" />
            <Satellite v-else class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-yellow-400'" />
            <span class="text-xs font-medium text-gray-200 truncate flex-1">{{ card.id }}</span>
            <Wifi v-if="!card.stale && card.signal >= -85" class="w-3 h-3 text-green-400 shrink-0" />
            <WifiOff v-else class="w-3 h-3 text-red-400 shrink-0" />
          </div>
          <div class="grid grid-cols-2 gap-x-3 gap-y-1 text-[10px]">
            <div class="flex justify-between"><span class="text-gray-500">Bat</span><span :class="batteryColor(card.battery)">{{ card.battery.toFixed(0) }}%</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Alt</span><span class="text-gray-300">{{ card.altitude.toFixed(0) }}m</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Spd</span><span class="text-gray-300">{{ card.speed.toFixed(1) }}m/s</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Sig</span><span :class="signalColor(card.signal)">{{ card.signal.toFixed(0) }}dBm</span></div>
          </div>
          <div v-if="card.stale" class="mt-1 text-[9px] text-red-400/80">No data > 4s</div>
          <div v-else-if="card.signal < -85" class="mt-1 text-[9px] text-yellow-400/80">Weak signal</div>
        </div>
      </div>
      <div v-if="selectedDevice && chartData" class="bg-gray-900/80 rounded-lg border border-gray-700 p-2" style="min-height: 200px">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-[10px] font-semibold text-gray-200">{{ selectedDevice }}</span>
          <button @click="selectedDevice = null" class="text-gray-500 hover:text-gray-300"><X class="w-3.5 h-3.5" /></button>
        </div>
        <div class="grid grid-cols-2 gap-2" style="height: 170px">
          <div v-for="item in [{ t: 'Alt', d: chartData.altitude, c: '#22d3ee' }, { t: 'Speed', d: chartData.speed, c: '#34d399' }, { t: 'Battery', d: chartData.battery, c: '#fbbf24' }, { t: 'Signal', d: chartData.signal, c: '#f472b6' }]" :key="item.t" class="bg-gray-900 rounded p-1 flex flex-col">
            <div class="text-[9px] text-gray-500 mb-0.5">{{ item.t }}</div>
            <div class="flex-1 min-h-0"><Line :data="item.d" :options="chartOptions" /></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
