<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard, MapIcon, LineChart, Video, TriangleAlert,
  HardDrive, Cable, BatteryWarning, ScrollText, Server, Settings, ChevronDown,
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()

interface NavItem {
  name: string
  path?: string
  icon?: any
  children?: NavItem[]
}

const navGroups = ref<{ label: string; items: NavItem[] }[]>([
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
])

const expandedGroups = ref<Set<string>>(new Set(['임무', '관측']))

function toggleGroup(label: string) {
  if (expandedGroups.value.has(label)) expandedGroups.value.delete(label)
  else expandedGroups.value.add(label)
}

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
        <div
          v-if="group.label"
          @click="toggleGroup(group.label)"
          class="flex items-center gap-1 px-4 py-1.5 text-[10px] font-semibold text-gray-600 uppercase tracking-wider cursor-pointer select-none hover:text-gray-400"
        >
          <ChevronDown class="w-3 h-3 transition-transform" :class="expandedGroups.has(group.label) ? '' : '-rotate-90'" />
          {{ group.label }}
        </div>
        <template v-if="!group.label || expandedGroups.has(group.label)">
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
        </template>
      </div>
    </nav>
  </aside>
</template>
