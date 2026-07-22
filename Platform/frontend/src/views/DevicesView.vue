<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Plane, Satellite, Search, X } from '@lucide/vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js'
import { useTelemetryService } from '@/services/telemetryService'
import { useDeviceService } from '@/services/deviceService'
import { fmtTime, fmtBattery } from '@/lib/format'
import { commandApi } from '@/lib/api/commands'
import OverlayPanel from '@/components/OverlayPanel.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const telemetry = useTelemetryService()
const device = useDeviceService()

type Tab = 'drones' | 'gateways'
const activeTab = ref<Tab>('drones')
const searchQuery = ref('')
const selectedId = ref<string | null>(null)

const filteredDrones = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return device.drones.filter((d: any) => d.id.toLowerCase().includes(q))
})

const selectedHistory = computed(() => {
  if (!selectedId.value || activeTab.value !== 'drones') return []
  return device.historyOf(selectedId.value).slice(-40)
})

const chartOptions = {
  responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
  scales: { x: { display: false }, y: { display: true, ticks: { color: '#6b7280', font: { size: 9 }, maxTicksLimit: 4 }, grid: { color: '#374151' }, beginAtZero: true } },
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
}

function makeChartData(values: number[], color: string, fillColor: string) {
  return { labels: values.map(() => ''), datasets: [{ data: values, borderColor: color, backgroundColor: fillColor, borderWidth: 1.5, pointRadius: 0, fill: true, tension: 0.3 }] }
}

const chartData = computed(() => {
  const h = selectedHistory.value
  return {
    altitude: makeChartData(h.map(t => t.altitude), '#22d3ee', 'rgba(34,211,238,0.08)'),
    speed: makeChartData(h.map(t => t.speed), '#34d399', 'rgba(52,211,153,0.08)'),
    battery: makeChartData(h.map(t => t.battery_level), '#fbbf24', 'rgba(251,191,36,0.08)'),
    heading: makeChartData(h.map(t => t.yaw), '#f472b6', 'rgba(244,114,182,0.08)'),
  }
})

const selectedTelemetry = computed(() => {
  if (!selectedId.value || activeTab.value !== 'drones') return null
  return telemetry.latestOf(selectedId.value)
})

const commands = ref<any[]>([])
const commandsLoading = ref(false)

async function loadCommands() {
  const id = selectedId.value
  if (!id) return
  commandsLoading.value = true
  try { const { data } = await commandApi.list(); commands.value = data }
  finally { commandsLoading.value = false }
}

watch(selectedId, () => { if (selectedId.value) loadCommands() })

const commandChains = computed(() => {
  const parents = commands.value.filter((c: any) => !c.parent_command_id)
  return parents.map((p: any) => ({ parent: p, child: commands.value.find((c: any) => c.parent_command_id === p.id) ?? null }))
})

function statusColor(s: string) { return { FLYING: 'text-green-400', LANDING: 'text-yellow-400', IDLE: 'text-gray-400', CHARGING: 'text-cyan-400', OFFLINE: 'text-red-400' }[s] ?? 'text-gray-400' }
function batteryColor(b: number) { return b > 60 ? 'text-green-400' : b > 30 ? 'text-yellow-400' : 'text-red-400' }

onMounted(() => { telemetry.start(); device.fetchGateways() })
onUnmounted(() => { telemetry.stop() })
</script>

<template>
  <OverlayPanel>
    <div class="flex items-center justify-between mb-3">
      <span class="text-[11px] font-semibold text-gray-500 uppercase">Devices</span>
    </div>
    <div class="flex items-center gap-2 mb-3">
      <div class="relative flex-1">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500" />
        <input v-model="searchQuery" type="text" placeholder="Search..." class="w-full h-7 pl-7 pr-2 bg-gray-900 border border-gray-700 rounded text-xs text-gray-200 placeholder-gray-500 outline-none focus:border-gray-500" />
      </div>
      <div class="flex gap-0.5 bg-gray-900 rounded p-0.5">
        <button @click="activeTab = 'drones'; selectedId = null" class="px-2.5 py-1 rounded text-[10px] font-medium transition-colors" :class="activeTab === 'drones' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Plane class="w-3 h-3 inline mr-1" />Drones</button>
        <button @click="activeTab = 'gateways'; selectedId = null" class="px-2.5 py-1 rounded text-[10px] font-medium transition-colors" :class="activeTab === 'gateways' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Satellite class="w-3 h-3 inline mr-1" />GW</button>
      </div>
    </div>

    <!-- Drone list -->
    <div v-if="activeTab === 'drones'">
      <div v-if="filteredDrones.length === 0" class="text-gray-500 text-xs text-center py-8">No drones found.</div>
      <div v-else class="space-y-1.5">
        <div v-for="d in filteredDrones" :key="d.id" @click="selectedId = selectedId === d.id ? null : d.id"
          class="flex items-center gap-3 px-3 py-2 bg-gray-900/80 rounded-lg border cursor-pointer transition-colors hover:border-gray-600"
          :class="selectedId === d.id ? 'border-gray-500' : 'border-gray-700'">
          <Plane class="w-4 h-4 text-gray-400 shrink-0" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-100">{{ d.id }}</span>
              <span class="text-[10px] text-gray-500">{{ d.model }}</span>
            </div>
            <div class="text-[10px] text-gray-500">GW {{ d.gateway }}</div>
          </div>
          <div class="text-right shrink-0">
            <div class="text-sm font-bold" :class="batteryColor(d.battery)">{{ fmtBattery(d.battery) }}</div>
            <div class="text-[10px]" :class="statusColor(d.status)">{{ d.status }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gateway list -->
    <div v-if="activeTab === 'gateways'">
      <div v-if="device.gateways.length === 0" class="text-gray-500 text-xs text-center py-8">No gateways.</div>
      <div v-else class="space-y-1.5">
        <div v-for="g in device.gateways" :key="g.id" @click="selectedId = selectedId === g.id ? null : g.id"
          class="flex items-center gap-3 px-3 py-2 bg-gray-900/80 rounded-lg border cursor-pointer transition-colors hover:border-gray-600"
          :class="selectedId === g.id ? 'border-gray-500' : 'border-gray-700'">
          <Satellite class="w-4 h-4 text-gray-400 shrink-0" />
          <div class="flex-1"><div class="text-xs font-semibold text-gray-100">{{ g.id }}</div><div class="text-[10px] text-gray-500">{{ g.name }}</div></div>
          <span class="text-xs" :class="g.status === 'online' ? 'text-green-400' : 'text-red-400'">{{ g.status }}</span>
        </div>
      </div>
    </div>

    <!-- Detail panel -->
    <div v-if="selectedId && activeTab === 'drones'" class="mt-3 border-t border-gray-700 pt-3 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-100">{{ selectedId }}</h3>
        <button @click="selectedId = null" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
      </div>

      <div v-if="selectedTelemetry" class="grid grid-cols-2 gap-2">
        <div class="bg-gray-900/60 rounded px-2 py-1 flex justify-between"><span class="text-[10px] text-gray-500">Pitch</span><span class="text-[10px] text-gray-200">{{ selectedTelemetry.pitch.toFixed(1) }}°</span></div>
        <div class="bg-gray-900/60 rounded px-2 py-1 flex justify-between"><span class="text-[10px] text-gray-500">Roll</span><span class="text-[10px] text-gray-200">{{ selectedTelemetry.roll.toFixed(1) }}°</span></div>
        <div class="bg-gray-900/60 rounded px-2 py-1 flex justify-between"><span class="text-[10px] text-gray-500">Yaw</span><span class="text-[10px] text-gray-200">{{ selectedTelemetry.yaw.toFixed(1) }}°</span></div>
        <div class="bg-gray-900/60 rounded px-2 py-1 flex justify-between"><span class="text-[10px] text-gray-500">Signal</span><span class="text-[10px] text-gray-200">{{ selectedTelemetry.signal_strength.toFixed(0) }}dBm</span></div>
      </div>
      <div v-else class="text-[10px] text-gray-600">Waiting for data...</div>

      <div class="grid grid-cols-2 gap-2" style="min-height: 140px">
        <div v-for="(item, idx) in [{ t: 'Alt', d: chartData.altitude, c: '#22d3ee' }, { t: 'Speed', d: chartData.speed, c: '#34d399' }, { t: 'Battery', d: chartData.battery, c: '#fbbf24' }, { t: 'Heading', d: chartData.heading, c: '#f472b6' }]" :key="idx" class="bg-gray-900/60 rounded p-1.5 flex flex-col">
          <div class="text-[9px] text-gray-500 mb-0.5">{{ item.t }}</div>
          <div class="flex-1 min-h-0"><Line v-if="item.d.datasets[0].data.length > 1" :data="item.d as any" :options="chartOptions" /><div v-else class="flex items-center justify-center h-full text-gray-600 text-[9px]">...</div></div>
        </div>
      </div>

      <div class="text-gray-500 text-[11px] pt-2 border-t border-gray-700">Command Chain</div>
      <div v-if="commandsLoading" class="text-[10px] text-gray-600">Loading...</div>
      <div v-else-if="commandChains.length === 0" class="text-[10px] text-gray-600">No commands</div>
      <div v-else class="space-y-2">
        <div v-for="chain in commandChains" :key="chain.parent.id" class="bg-gray-900/60 rounded px-2 py-1.5">
          <div class="flex items-center justify-between mb-1"><span class="text-xs font-semibold text-gray-200">{{ chain.parent.type }}</span><span class="text-[9px] text-gray-500">{{ chain.parent.issuer }}</span></div>
          <div class="text-[9px] text-gray-500 mb-1">{{ fmtTime(chain.parent.issued_at) }}</div>
          <div class="flex items-center gap-1 text-[9px]">
            <span class="text-cyan-400">Server</span>
            <span class="text-[8px] px-1 bg-gray-800 rounded" :class="chain.parent.status === 'SUCCEEDED' ? 'text-green-400' : chain.parent.status === 'FAILED' ? 'text-red-400' : 'text-gray-400'">{{ chain.parent.status }}</span>
            <span class="text-gray-400">{{ chain.parent.target_id }}</span>
            <template v-if="chain.child">
              <span class="text-gray-600">&rarr;</span>
              <span class="text-gray-400">{{ chain.child.target_id }}</span>
              <span class="text-[8px] px-1 bg-gray-800 rounded" :class="chain.child.status === 'SUCCEEDED' ? 'text-green-400' : chain.child.status === 'FAILED' ? 'text-red-400' : 'text-gray-400'">{{ chain.child.status }}</span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </OverlayPanel>
</template>
