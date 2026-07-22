<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import DashboardBase from '@/components/DashboardBase.vue'

const route = useRoute()
const isDashboard = computed(() => route.path === '/dashboard')
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <Sidebar />
    <main class="flex-1 flex min-h-0">
      <!-- Left: Dashboard base (always visible) -->
      <div class="flex flex-col min-h-0 transition-all duration-300" :class="isDashboard ? 'flex-1' : 'w-1/2'">
        <DashboardBase :mini="!isDashboard" />
        <router-view v-if="isDashboard" class="flex-1 min-h-0" />
      </div>
      <!-- Right: Overlay panel on non-dashboard routes -->
      <transition name="slide-panel">
        <router-view
          v-if="!isDashboard"
          class="w-1/2 bg-[#1a1a1a] border-l border-gray-800 flex flex-col min-h-0"
        />
      </transition>
    </main>
  </div>
</template>

<style scoped>
.slide-panel-enter-active, .slide-panel-leave-active {
  transition: width 0.25s ease, opacity 0.25s ease;
}
.slide-panel-enter-from, .slide-panel-leave-to {
  width: 0 !important;
  opacity: 0;
  overflow: hidden;
}
</style>
