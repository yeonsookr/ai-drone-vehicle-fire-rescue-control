<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard, MapIcon, LineChart, HardDrive, Settings,
} from '@lucide/vue'

defineProps<{ connected: boolean }>()

const route = useRoute()
const router = useRouter()

interface NavItem {
  name: string
  path?: string
  icon?: any
}

const navGroups: { label: string; items: NavItem[] }[] = [
  { label: '', items: [{ name: '대시보드', path: '/dashboard', icon: LayoutDashboard }] },
  {
    label: '임무',
    items: [
      { name: '임무 목록', path: '/missions', icon: MapIcon },
    ],
  },
  {
    label: '관측',
    items: [
      { name: '텔레메트리', path: '/telemetry', icon: LineChart },
    ],
  },
  {
    label: '장비',
    items: [
      { name: '장비 목록', path: '/devices', icon: HardDrive },
    ],
  },
  {
    label: '시스템',
    items: [
      { name: '설정', path: '/system/settings', icon: Settings },
    ],
  },
]

function isActive(path?: string) {
  if (!path) return false
  return route.path.startsWith(path)
}

function navigate(path?: string) {
  if (path) router.push(path)
}
</script>

<template>
  <aside class="w-56 shrink-0 border-r border-gray-800 flex flex-col bg-[#1a1a1a]">
    <div class="h-14 flex items-center justify-between px-4 border-b border-gray-800">
      <span class="text-[11px] font-bold tracking-widest text-gray-500 uppercase">AIoT CTRL</span>
      <span class="text-[10px]" :class="connected ? 'text-green-400' : 'text-red-400'">{{ connected ? '● Connected' : '○ Disconnected' }}</span>
    </div>
    <nav class="flex-1 overflow-y-auto py-2">
      <div v-for="group in navGroups" :key="group.label" class="mb-1">
        <div v-if="group.label" class="px-4 py-1.5 text-[10px] font-semibold text-gray-600 uppercase tracking-wider select-none">
          {{ group.label }}
        </div>
        <button
          v-for="item in group.items"
          :key="item.name"
          @click="navigate(item.path)"
          class="w-full flex items-center gap-3 px-4 py-2 text-sm text-left transition-colors duration-150"
          :class="isActive(item.path) ? 'text-gray-100 bg-gray-800/60 border-l-2 border-gray-400' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800/30'"
        >
          <component :is="item.icon" v-if="item.icon" class="w-4 h-4 shrink-0" />
          {{ item.name }}
        </button>
      </div>
    </nav>
  </aside>
</template>
