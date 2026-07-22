<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Plane, Satellite, Search, Plus, X } from '@lucide/vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js'
import { useTelemetryService } from '@/services/telemetryService'
import { useDeviceService } from '@/services/deviceService'
import { fmtCoord, fmtTime, fmtBattery } from '@/lib/format'
import { commandApi } from '@/lib/api/commands'

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

const filteredGateways = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return device.gateways.filter((g: any) => g.id.toLowerCase().includes(q) || g.name.toLowerCase().includes(q))
})

const selectedItem = computed(() => {
  if (!selectedId.value) return null
  if (activeTab.value === 'drones') return filteredDrones.value.find((d) => d.id === selectedId.value) ?? null
  return filteredGateways.value.find((g) => g.id === selectedId.value) ?? null
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

function select(id: string) { selectedId.value = selectedId.value === id ? null : id }

function statusLabel(s: string) { return { FLYING: 'Flying', LANDING: 'Landing', IDLE: 'Idle', CHARGING: 'Charging', OFFLINE: 'Offline' }[s] ?? s }
function statusColor(s: string) { return { FLYING: 'text-green-400', LANDING: 'text-yellow-400', IDLE: 'text-gray-400', CHARGING: 'text-cyan-400', OFFLINE: 'text-red-400' }[s] ?? 'text-gray-400' }
function batteryColor(b: number) { return b > 60 ? 'text-green-400' : b > 30 ? 'text-yellow-400' : 'text-red-400' }

const commands = ref<any[]>([])
const commandsLoading = ref(false)

async function loadCommands() {
  const id = selectedId.value
  if (!id) return
  commandsLoading.value = true
  try {
    const { data } = await commandApi.list()
    commands.value = data
  } finally { commandsLoading.value = false }
}

watch(selectedId, () => { if (selectedId.value) loadCommands() })

const commandChains = computed(() => {
  const parents = commands.value.filter((c: any) => !c.parent_command_id)
  return parents.map((p: any) => {
    const child = commands.value.find((c: any) => c.parent_command_id === p.id) ?? null
    return { parent: p, child }
  })
})

function hopStatus(s: string) {
  return { SUCCEEDED: 'text-green-400', FAILED: 'text-red-400', RUNNING: 'text-yellow-400', ACK: 'text-cyan-400', EXPIRED: 'text-gray-500' }[s] ?? 'text-gray-500'
}

function hopIcon(s: string) {
  return s === 'SUCCEEDED' ? 'OK' : s === 'FAILED' ? 'FAIL' : s === 'RUNNING' ? '...' : s
}

onMounted(() => { telemetry.start(); device.fetchGateways() })
onUnmounted(() => { telemetry.stop() })
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <div class="h-14 flex items-center justify-between px-6 border-b border-gray-800 shrink-0">
      <h1 class="text-base font-bold text-gray-100">Devices</h1>
      <div class="flex items-center gap-3">
        <span class="text-xs px-2 py-0.5 rounded-full" :class="device.connected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'">{{ device.connected ? '● Live' : '○ Offline' }}</span>
        <button class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-400 transition-colors"><Plus class="w-3.5 h-3.5" /> Add Device</button>
      </div>
    </div>
    <div class="flex items-center gap-4 px-6 py-2.5 border-b border-gray-800 shrink-0">
      <div class="relative flex-1 max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
        <input v-model="searchQuery" type="text" placeholder="Search devices..." class="w-full h-8 pl-9 pr-3 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-200 placeholder-gray-500 outline-none focus:border-gray-500 transition-colors" />
      </div>
      <div class="flex gap-1 bg-gray-800 rounded-lg p-0.5">
        <button @click="activeTab = 'drones'; selectedId = null" class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors" :class="activeTab === 'drones' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Plane class="w-3.5 h-3.5" /> Drones ({{ device.drones.length }})</button>
        <button @click="activeTab = 'gateways'; selectedId = null" class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors" :class="activeTab === 'gateways' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Satellite class="w-3.5 h-3.5" /> Gateways ({{ device.gateways.length }})</button>
      </div>
    </div>
    <div class="flex-1 flex min-h-0">
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="activeTab === 'drones' && filteredDrones.length === 0" class="flex items-center justify-center h-full text-gray-500 text-xs">No drones found.</div>
        <div v-if="activeTab === 'gateways' && filteredGateways.length === 0" class="flex items-center justify-center h-full text-gray-500 text-xs">No gateways found.</div>
        <div v-if="activeTab === 'drones'" class="space-y-2">
          <div v-for="d in filteredDrones" :key="d.id" @click="select(d.id)" class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600" :class="{ 'border-gray-500': selectedId === d.id }">
            <Plane class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2"><span class="text-sm font-semibold text-gray-100">{{ d.id }}</span><span class="text-xs text-gray-500">{{ d.model }}</span></div>
              <div class="flex items-center gap-3 mt-1 text-xs text-gray-500"><span>GW {{ d.gateway }}</span><span v-if="d.lat">{{ fmtCoord(d.lat, d.lng) }}</span></div>
            </div>
            <div class="text-right shrink-0"><div class="text-sm font-bold" :class="batteryColor(d.battery)">{{ fmtBattery(d.battery) }}</div><div class="text-xs" :class="statusColor(d.status)">{{ statusLabel(d.status) }}</div></div>
          </div>
        </div>
        <div v-else class="space-y-2">
          <div v-for="g in filteredGateways" :key="g.id" @click="select(g.id)" class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600" :class="{ 'border-gray-500': selectedId === g.id }">
            <Satellite class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0"><div class="flex items-center gap-2"><span class="text-sm font-semibold text-gray-100">{{ g.id }}</span><span class="text-xs text-gray-500">{{ g.name }}</span></div><div class="text-xs text-gray-500 mt-1">{{ g.ip_address }}</div></div>
            <div class="text-right shrink-0"><div class="flex items-center gap-1 justify-end text-xs text-gray-400"><Satellite class="w-3 h-3" :class="g.status === 'online' ? 'text-green-400' : 'text-red-400'" /> {{ g.status }}</div></div>
          </div>
        </div>
      </div>
      <Transition name="slide">
        <div v-if="selectedItem && activeTab === 'drones'" class="w-96 border-l border-gray-800 flex flex-col bg-gray-850">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800 shrink-0"><h3 class="text-sm font-semibold text-gray-100">{{ selectedItem.id }}</h3><button @click="selectedId = null" class="text-gray-500 hover:text-gray-300 transition-colors"><X class="w-4 h-4" /></button></div>
          <div class="flex-1 px-5 py-4 text-xs overflow-y-auto space-y-3">
            <div class="flex justify-between"><span class="text-gray-500">Model</span><span class="text-gray-200">{{ (selectedItem as any).model }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Gateway</span><span class="text-gray-200">{{ (selectedItem as any).gateway }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Battery</span><span class="text-gray-200" :class="batteryColor((selectedItem as any).battery)">{{ fmtBattery((selectedItem as any).battery) }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor((selectedItem as any).status)">{{ statusLabel((selectedItem as any).status) }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Latitude</span><span class="text-gray-200 font-mono">{{ fmtCoord((selectedItem as any).lat, (selectedItem as any).lng) }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Longitude</span><span class="text-gray-200 font-mono">{{ (selectedItem as any).lng.toFixed(6) }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Last Seen</span><span class="text-gray-200">{{ fmtTime((selectedItem as any).updatedAt) }}</span></div>
            <div class="text-gray-500 text-xs pt-2 border-t border-gray-800">Metrics (recent 40s)</div>
            <div class="grid grid-cols-2 grid-rows-2 gap-2" style="min-height: 300px">
              <div v-for="(item, idx) in [{ title: 'Alt', data: chartData.altitude, color: '#22d3ee' }, { title: 'Speed', data: chartData.speed, color: '#34d399' }, { title: 'Battery', data: chartData.battery, color: '#fbbf24' }, { title: 'Heading', data: chartData.heading, color: '#f472b6' }]" :key="idx" class="bg-gray-900 rounded p-1.5 flex flex-col">
                <div class="text-[10px] text-gray-500 mb-0.5">{{ item.title }}</div>
                <div class="flex-1 min-h-0"><Line v-if="item.data.datasets[0].data.length > 1" :data="item.data as any" :options="chartOptions" /><div v-else class="flex items-center justify-center h-full text-gray-600 text-[10px]">...</div></div>
              </div>
            </div>
            <div class="text-gray-500 text-xs pt-2 border-t border-gray-800">Command Chain</div>
            <div v-if="commandsLoading" class="text-xs text-gray-600">Loading...</div>
            <div v-else-if="commandChains.length === 0" class="text-xs text-gray-600">No commands</div>
            <div v-else class="space-y-2">
              <div v-for="chain in commandChains" :key="chain.parent.id" class="bg-gray-900 rounded px-3 py-2">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-semibold text-gray-200">{{ chain.parent.type }}</span>
                  <span class="text-[10px] text-gray-500">{{ chain.parent.issuer }}</span>
                </div>
                <div class="text-[10px] text-gray-500 mb-2">{{ fmtTime(chain.parent.issued_at) }}</div>
                <div class="flex items-center gap-1 text-[10px]">
                  <div class="flex flex-col items-center">
                    <div class="w-2 h-2 rounded-full bg-cyan-400"></div>
                    <div class="text-cyan-400 mt-0.5">Server</div>
                  </div>
                  <div class="flex-1 h-px bg-gray-700 relative">
                    <span class="absolute -top-3 left-1/2 -translate-x-1/2 text-[9px] whitespace-nowrap" :class="hopStatus(chain.parent.status)">{{ hopIcon(chain.parent.status) }}</span>
                  </div>
                  <div class="flex flex-col items-center">
                    <div class="w-2 h-2 rounded-full" :class="chain.parent.status === 'SUCCEEDED' ? 'bg-green-400' : chain.parent.status === 'FAILED' ? 'bg-red-400' : 'bg-gray-500'"></div>
                    <div class="text-gray-400 mt-0.5">{{ chain.parent.target_id }}</div>
                  </div>
                  <template v-if="chain.child">
                    <div class="flex-1 h-px bg-gray-700 relative">
                      <span class="absolute -top-3 left-1/2 -translate-x-1/2 text-[9px] whitespace-nowrap" :class="hopStatus(chain.child.status)">{{ hopIcon(chain.child.status) }}</span>
                    </div>
                    <div class="flex flex-col items-center">
                      <div class="w-2 h-2 rounded-full" :class="chain.child.status === 'SUCCEEDED' ? 'bg-green-400' : chain.child.status === 'FAILED' ? 'bg-red-400' : 'bg-gray-500'"></div>
                      <div class="text-gray-400 mt-0.5">{{ chain.child.target_id }}</div>
                    </div>
                  </template>
                </div>
                <div v-if="chain.child && chain.child.error_reason" class="text-[9px] text-red-400 mt-1">{{ chain.child.error_reason }}</div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
      <Transition name="slide">
        <div v-if="selectedItem && activeTab === 'gateways'" class="w-96 border-l border-gray-800 overflow-y-auto shrink-0 flex flex-col bg-gray-850">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800 shrink-0"><h3 class="text-sm font-semibold text-gray-100">{{ (selectedItem as any).id }}</h3><button @click="selectedId = null" class="text-gray-500 hover:text-gray-300 transition-colors"><X class="w-4 h-4" /></button></div>
          <div class="flex-1 px-5 py-4 text-xs space-y-3">
            <div class="flex justify-between"><span class="text-gray-500">Name</span><span class="text-gray-200">{{ (selectedItem as any).name }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">IP Address</span><span class="text-gray-200 font-mono">{{ (selectedItem as any).ip_address }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="(selectedItem as any).status === 'online' ? 'text-green-400' : 'text-red-400'">{{ (selectedItem as any).status }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Last Heartbeat</span><span class="text-gray-200">{{ (selectedItem as any).last_heartbeat_at }}</span></div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: width 0.2s ease, opacity 0.2s ease; }
.slide-enter-from, .slide-leave-to { width: 0 !important; opacity: 0; overflow: hidden; }
</style>
