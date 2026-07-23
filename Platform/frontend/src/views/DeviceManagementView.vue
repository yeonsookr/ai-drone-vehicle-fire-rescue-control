<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plane, Satellite, Plus, Pencil, Trash2, X, Check } from '@lucide/vue'
import { droneApi } from '@/lib/api/drones'
import { vehicleApi } from '@/lib/api/vehicles'
import OverlayPanel from '@/components/OverlayPanel.vue'
import PanelSection from '@/components/PanelSection.vue'

type Tab = 'drones' | 'vehicles'
const activeTab = ref<Tab>('drones')
const items = ref<Record<Tab, any[]>>({ drones: [], vehicles: [] })
const editing = ref<any | null>(null)
const showForm = ref(false)

onMounted(async () => {
  const [dr, ve] = await Promise.all([droneApi.list(), vehicleApi.list()])
  items.value.drones = dr.data
  items.value.vehicles = ve.data
})

const currentItems = computed(() => items.value[activeTab.value])

const formConfig: Record<Tab, { key: string; label: string; type: 'text' | 'select'; options?: string[] }[]> = {
  drones: [
    { key: 'name', label: 'Name', type: 'text' },
    { key: 'status', label: 'Status', type: 'select', options: ['flying', 'docked', 'returning', 'landing', 'error'] },
    { key: 'type', label: 'Type', type: 'select', options: ['real', 'mock'] },
  ],
  vehicles: [
    { key: 'name', label: 'Name', type: 'text' },
    { key: 'status', label: 'Status', type: 'select', options: ['moving', 'idle', 'stopped', 'error'] },
    { key: 'type', label: 'Type', type: 'select', options: ['real', 'mock'] },
  ],
}

function startCreate() {
  editing.value = { id: '', name: '', status: '', type: 'mock', battery_level: 0 }
  showForm.value = true
}

function startEdit(item: any) {
  editing.value = { ...item }
  showForm.value = true
}

function save() {
  if (!editing.value) return
  const list = items.value[activeTab.value]
  const idx = list.findIndex((x: any) => x.id === editing.value.id)
  if (idx >= 0) list[idx] = { ...list[idx], ...editing.value }
  else list.push({ ...editing.value })
  showForm.value = false
  editing.value = null
}

function remove(id: string) {
  if (!confirm(`Delete ${id}?`)) return
  items.value[activeTab.value] = items.value[activeTab.value].filter((x: any) => x.id !== id)
}
</script>

<template>
  <OverlayPanel>
    <PanelSection label="Device Management">
      <template #badge>
        <button @click="startCreate" class="flex items-center gap-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-[10px] text-gray-200 transition-colors"><Plus class="w-3 h-3" /> Add</button>
      </template>
    </PanelSection>

    <div class="flex gap-0.5 mb-3 p-0.5 bg-gray-800 rounded-lg w-fit">
      <button @click="activeTab = 'drones'" class="px-3 py-1 text-[10px] rounded-md font-medium transition-colors" :class="activeTab === 'drones' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Plane class="w-3 h-3 inline mr-1" />Drones ({{ items.drones.length }})</button>
      <button @click="activeTab = 'vehicles'" class="px-3 py-1 text-[10px] rounded-md font-medium transition-colors" :class="activeTab === 'vehicles' ? 'bg-gray-700 text-gray-200' : 'text-gray-500 hover:text-gray-300'"><Satellite class="w-3 h-3 inline mr-1" />Vehicles ({{ items.vehicles.length }})</button>
    </div>

    <div v-if="currentItems.length === 0" class="text-gray-500 text-xs text-center py-8">No devices registered.</div>
    <div v-else class="space-y-1.5">
      <div v-for="item in currentItems" :key="item.id" class="flex items-center gap-2 px-3 py-2 bg-gray-900/80 rounded-lg border border-gray-700">
        <Plane v-if="activeTab === 'drones'" class="w-4 h-4 text-cyan-400 shrink-0" />
        <Satellite v-else class="w-4 h-4 text-yellow-400 shrink-0" />
        <div class="flex-1 min-w-0">
          <div class="text-xs font-semibold text-gray-100">{{ item.id }}</div>
          <div class="text-[10px] text-gray-500 truncate">{{ item.name }} · {{ item.status }} · {{ item.type }}</div>
        </div>
        <button @click="startEdit(item)" class="p-1 text-gray-500 hover:text-gray-300"><Pencil class="w-3.5 h-3.5" /></button>
        <button @click="remove(item.id)" class="p-1 text-gray-500 hover:text-red-400"><Trash2 class="w-3.5 h-3.5" /></button>
      </div>
    </div>

    <div v-if="showForm && editing" class="mt-3 border-t border-gray-700 pt-3 space-y-2">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-semibold text-gray-200">{{ editing.id ? 'Edit' : 'Add' }} {{ activeTab.slice(0, -1) }}</span>
        <button @click="showForm = false; editing = null" class="text-gray-500 hover:text-gray-300"><X class="w-4 h-4" /></button>
      </div>
      <div class="flex justify-between items-center text-[11px]"><span class="text-gray-500">ID</span><input v-model="editing.id" class="w-40 bg-gray-900 border border-gray-700 rounded px-2 py-0.5 text-[11px] text-gray-200 text-right" /></div>
      <div v-for="f in formConfig[activeTab]" :key="f.key" class="flex justify-between items-center text-[11px]">
        <span class="text-gray-500">{{ f.label }}</span>
        <select v-if="f.type === 'select'" v-model="editing[f.key]" class="w-40 bg-gray-900 border border-gray-700 rounded px-2 py-0.5 text-[11px] text-gray-200 text-right">
          <option v-for="o in f.options" :key="o" :value="o">{{ o }}</option>
        </select>
        <input v-else v-model="editing[f.key]" class="w-40 bg-gray-900 border border-gray-700 rounded px-2 py-0.5 text-[11px] text-gray-200 text-right" />
      </div>
      <button @click="save" class="w-full py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-200 transition-colors flex items-center justify-center gap-1"><Check class="w-3.5 h-3.5" /> Save</button>
    </div>
  </OverlayPanel>
</template>
