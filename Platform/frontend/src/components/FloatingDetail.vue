<script setup lang="ts">
import { computed, ref } from 'vue'
import { X } from '@lucide/vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js'
import { useDeviceService } from '@/services/deviceService'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const props = defineProps<{ deviceId: string }>()
const emit = defineEmits<{ close: [] }>()

const device = useDeviceService()
const activeTab = ref<'charts' | 'commands'>('charts')

const history = computed(() => device.deviceHistoryOf(props.deviceId).slice(-60))

const chartOptions = {
  responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
  scales: { x: { display: false }, y: { display: true, ticks: { color: '#6b7280', font: { size: 8 }, maxTicksLimit: 4 }, grid: { color: '#374151' }, beginAtZero: true } },
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
}

function makeData(values: number[], color: string) {
  return { labels: values.map(() => ''), datasets: [{ data: values, borderColor: color, backgroundColor: color.replace(')', ',0.08)').replace('rgb', 'rgba'), borderWidth: 1.5, pointRadius: 0, fill: true, tension: 0.3 }] }
}

const chartData = computed(() => {
  const h = history.value
  return {
    altitude: makeData(h.map(t => t.altitude), '#22d3ee'),
    speed: makeData(h.map(t => t.speed), '#34d399'),
    battery: makeData(h.map(t => t.battery_level), '#fbbf24'),
    heading: makeData(h.map(t => t.yaw), '#f472b6'),
  }
})

const card = computed(() => device.equipmentCards.find(c => c.id === props.deviceId) ?? null)
</script>

<template>
  <div class="w-96 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden max-h-[80vh]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-gray-100">{{ deviceId }}</span>
        <span v-if="card" class="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">{{ card.type }}</span>
      </div>
      <button @click="emit('close')" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-0 border-b border-gray-700">
      <button @click="activeTab = 'charts'" class="flex-1 py-2 text-[10px] font-medium transition-colors" :class="activeTab === 'charts' ? 'text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-300'">Charts</button>
      <button @click="activeTab = 'commands'" class="flex-1 py-2 text-[10px] font-medium transition-colors" :class="activeTab === 'commands' ? 'text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-300'">Commands</button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-3 text-xs min-h-0">
      <!-- Charts tab -->
      <template v-if="activeTab === 'charts'">
        <div v-if="card" class="grid grid-cols-2 gap-x-4 gap-y-1 mb-3 p-2 bg-gray-800/60 rounded">
          <div class="flex justify-between"><span class="text-gray-500">Battery</span><span :class="card.battery > 60 ? 'text-green-400' : card.battery > 30 ? 'text-yellow-400' : 'text-red-400'">{{ card.battery.toFixed(0) }}%</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Signal</span><span :class="card.signal > -75 ? 'text-green-400' : card.signal > -85 ? 'text-yellow-400' : 'text-red-400'">{{ card.signal.toFixed(0) }}dBm</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Altitude</span><span class="text-gray-200">{{ card.altitude.toFixed(0) }}m</span></div>
          <div class="flex justify-between"><span class="text-gray-500">Speed</span><span class="text-gray-200">{{ card.speed.toFixed(1) }}m/s</span></div>
        </div>
        <div v-if="history.length < 2" class="text-gray-600 text-[10px] text-center py-8">Collecting data...</div>
        <div v-else class="grid grid-cols-2 gap-2" style="min-height: 200px">
          <div v-for="item in [{ t: 'Alt', d: chartData.altitude, c: '#22d3ee' }, { t: 'Speed', d: chartData.speed, c: '#34d399' }, { t: 'Battery', d: chartData.battery, c: '#fbbf24' }, { t: 'Heading', d: chartData.heading, c: '#f472b6' }]" :key="item.t" class="bg-gray-800/60 rounded p-1.5 flex flex-col">
            <div class="text-[9px] text-gray-500 mb-0.5">{{ item.t }}</div>
            <div class="flex-1 min-h-0"><Line v-if="item.d.datasets[0].data.length > 1" :data="item.d as any" :options="chartOptions" /><div v-else class="flex items-center justify-center h-full text-gray-600 text-[9px]">...</div></div>
          </div>
        </div>
      </template>

      <!-- Commands tab -->
      <template v-if="activeTab === 'commands'">
        <div class="text-gray-500 text-[10px] mb-2">Command history for {{ deviceId }}</div>
        <div class="text-gray-600 text-[10px] text-center py-8">No commands recorded.</div>
      </template>
    </div>
  </div>
</template>
