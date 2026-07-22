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
    <main class="flex-1 flex flex-col min-h-0 relative">
      <!-- Dashboard base: always visible, scaled down in overlay mode -->
      <DashboardBase :mini="!isDashboard" />
      <!-- Page content -->
      <div
        class="flex-1 min-h-0 transition-all duration-300"
        :class="isDashboard ? '' : 'absolute inset-0 z-10'"
      >
        <router-view />
      </div>
    </main>
  </div>
</template>
