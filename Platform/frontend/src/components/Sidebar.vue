<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard, MapIcon, LineChart, Settings,
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()

interface NavItem { name: string; path: string; icon: any }

const navItems: NavItem[] = [
  { name: '대시보드', path: '/dashboard', icon: LayoutDashboard },
  { name: '임무', path: '/missions', icon: MapIcon },
  { name: '장비', path: '/telemetry', icon: LineChart },
  { name: '설정', path: '/system/settings', icon: Settings },
]

function isActive(path: string) { return route.path === path }

function navigate(path: string) { router.push(path) }
</script>

<template>
  <nav class="flex gap-0">
    <button
      v-for="item in navItems" :key="item.path"
      @click="navigate(item.path)"
      class="flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] transition-colors"
      :class="isActive(item.path) ? 'text-gray-100 bg-gray-800/60' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800/30'"
    >
      <component :is="item.icon" class="w-4 h-4" />
      {{ item.name }}
    </button>
  </nav>
</template>
