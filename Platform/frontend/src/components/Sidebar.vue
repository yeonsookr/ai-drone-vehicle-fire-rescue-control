<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LayoutDashboard, HardDrive, LineChart, TriangleAlert } from '@lucide/vue'

const route = useRoute()
const router = useRouter()

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Devices', path: '/devices', icon: HardDrive },
  { name: 'Telemetry', path: '/telemetry', icon: LineChart },
  { name: 'Detections', path: '/detections', icon: TriangleAlert },
]

const activeIndex = computed(() => navItems.findIndex((n) => n.path === route.path))
</script>

<template>
  <aside class="w-56 shrink-0 border-r border-gray-800 flex flex-col bg-[#1a1a1a]">
    <div class="h-14 flex items-center px-4 border-b border-gray-800 text-sm font-bold tracking-wider text-gray-500">
      AIoT CTRL
    </div>
    <nav class="flex-1 py-2">
      <button
        v-for="(item, i) in navItems"
        :key="item.path"
        @click="router.push(item.path)"
        class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors duration-150"
        :class="i === activeIndex ? 'text-gray-100 bg-gray-800/60 border-l-2 border-gray-400' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800/30'"
      >
        <component :is="item.icon" class="w-4 h-4 shrink-0" />
        {{ item.name }}
      </button>
    </nav>
  </aside>
</template>
