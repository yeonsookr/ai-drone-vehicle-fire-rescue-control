<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDeviceService } from '@/services/deviceService'
import { Plane, Satellite, Wifi, WifiOff } from '@lucide/vue'
import OverlayPanel from '@/components/OverlayPanel.vue'
import PanelSection from '@/components/PanelSection.vue'

const router = useRouter()

const device = useDeviceService()
const filter = ref<'all' | 'drone' | 'vehicle'>('all')

const filteredCards = computed(() => {
  if (filter.value === 'all') return device.equipmentCards
  return device.equipmentCards.filter(c => c.type === filter.value)
})

function batteryColor(b: number) { return b > 60 ? 'text-green-400' : b > 30 ? 'text-yellow-400' : 'text-red-400' }
function signalColor(s: number) { return s > -75 ? 'text-green-400' : s > -85 ? 'text-yellow-400' : 'text-red-400' }
</script>

<template>
  <OverlayPanel>
    <PanelSection label="Devices">
      <template #badge><span v-if="device.disconnectedDevices.length > 0" class="text-[10px] px-2 py-0.5 rounded-full bg-red-900 text-red-300">! {{ device.disconnectedDevices.length }} disconnected</span></template>
    </PanelSection>

    <!-- Filter tabs -->
    <div class="flex gap-0.5 mb-3 p-0.5 bg-gray-800 rounded-lg w-fit">
      <button @click="filter = 'all'" class="px-3 py-1 text-[10px] rounded-md font-medium transition-colors" :class="filter === 'all' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'">All ({{ device.equipmentCards.length }})</button>
      <button @click="filter = 'drone'" class="px-3 py-1 text-[10px] rounded-md font-medium transition-colors" :class="filter === 'drone' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Plane class="w-3 h-3 inline mr-1" />Drones ({{ device.equipmentCards.filter(c => c.type === 'drone').length }})</button>
      <button @click="filter = 'vehicle'" class="px-3 py-1 text-[10px] rounded-md font-medium transition-colors" :class="filter === 'vehicle' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Satellite class="w-3 h-3 inline mr-1" />Vehicles ({{ device.equipmentCards.filter(c => c.type === 'vehicle').length }})</button>
    </div>

    <div v-if="filteredCards.length === 0" class="flex items-center justify-center h-20 text-gray-600 text-xs">Waiting for telemetry...</div>
    <div v-else class="grid grid-cols-2 gap-2">
      <div v-for="card in filteredCards" :key="card.id" @click="router.push({ query: { detail: card.id } })"
        class="bg-gray-900/80 rounded-lg border px-3 py-2 cursor-pointer transition-colors hover:border-gray-600"
        :class="[card.stale ? 'opacity-60' : 'border-gray-700']">
        <div class="flex items-center gap-2 mb-1.5">
          <Plane v-if="card.type === 'drone'" class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-cyan-400'" />
          <Satellite v-else class="w-3.5 h-3.5" :class="card.stale ? 'text-gray-600' : 'text-yellow-400'" />
          <span class="text-xs font-medium text-gray-200 truncate flex-1">{{ card.id }}</span>
          <Wifi v-if="!card.stale && card.signal >= -85" class="w-3 h-3 text-green-400 shrink-0" /><WifiOff v-else class="w-3 h-3 text-red-400 shrink-0" />
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
  </OverlayPanel>
</template>
