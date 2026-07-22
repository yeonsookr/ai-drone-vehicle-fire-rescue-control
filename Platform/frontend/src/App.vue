<script setup lang="ts">
import Sidebar from '@/components/Sidebar.vue'
import DashboardBase from '@/components/DashboardBase.vue'
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <Sidebar />
    <main class="flex-1 flex min-h-0">
      <!-- Left: Permanent dashboard base (map + stats) -->
      <div class="w-1/2 flex flex-col min-h-0 border-r border-gray-800">
        <DashboardBase />
      </div>
      <!-- Right: Content panel (page or overlay) -->
      <router-view class="flex-1 flex flex-col min-h-0" />
    </main>
  </div>
</template>
