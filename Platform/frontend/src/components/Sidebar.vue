<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard, MapIcon, LineChart, Video, TriangleAlert,
  HardDrive, Cable, BatteryWarning, ScrollText, Server, Settings,
} from '@lucide/vue'

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
      { name: '영상 스트림', path: '/streams', icon: Video },
      { name: 'AI 탐지', path: '/detections', icon: TriangleAlert },
    ],
  },
  {
    label: '장비',
    items: [
      { name: '장비 목록', path: '/devices', icon: HardDrive },
      { name: '페어링', path: '/pairings', icon: Cable },
    ],
  },
  {
    label: '운영',
    items: [
      { name: '배터리 현황', path: '/operations/battery', icon: BatteryWarning },
      { name: '운영 로그', path: '/operations/logs', icon: ScrollText },
    ],
  },
  {
    label: '시스템',
    items: [
      { name: '서버 상태', path: '/system/server', icon: Server },
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
    <div class="h-14 flex items-center px-4 border-b border-gray-800 text-[11px] font-bold tracking-widest text-gray-500 uppercase">
      AIoT CTRL
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
