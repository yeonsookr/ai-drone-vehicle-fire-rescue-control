<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import { PanelRightClose, PanelRightOpen, Maximize2, Minimize2 } from '@lucide/vue'
import Sidebar from '@/components/Sidebar.vue'
import MapPanel from '@/components/MapPanel.vue'

const telemetry = useTelemetryService()
const connected = computed(() => telemetry.connected)
const overlayVisible = ref(true)
const overlayExpanded = ref(false)

function toggleVisible() { overlayVisible.value = !overlayVisible.value }
function toggleExpand() { overlayExpanded.value = !overlayExpanded.value }
</script>

<template>
  <div class="flex h-screen bg-[#0f0f0f] text-gray-200">
    <Sidebar :connected="connected" />
    <main class="flex-1 relative min-h-0">
      <MapPanel class="absolute inset-0 z-0" />

      <!-- Overlay toggle button (always visible) -->
      <button
        @click="toggleVisible"
        class="absolute top-4 z-20 w-7 h-7 bg-gray-800/80 hover:bg-gray-700 rounded-l border border-gray-700 flex items-center justify-center text-gray-400 transition-colors"
        :class="overlayVisible ? 'right-[calc(20rem+1px)]' : 'right-4'"
        :title="overlayVisible ? 'Hide panel' : 'Show panel'"
      >
        <PanelRightClose v-if="overlayVisible" class="w-4 h-4" />
        <PanelRightOpen v-else class="w-4 h-4" />
      </button>

      <!-- Overlay panel -->
      <transition name="overlay-slide">
        <div
          v-if="overlayVisible"
          class="absolute top-4 bottom-4 z-10 flex pointer-events-none"
          :class="overlayExpanded ? 'right-4 w-1/2' : 'right-4 w-80'"
        >
          <!-- Expand toggle -->
          <button
            @click="toggleExpand"
            class="pointer-events-auto w-5 bg-gray-800/80 hover:bg-gray-700 rounded-l border border-r-0 border-gray-700 flex items-center justify-center text-gray-400 transition-colors cursor-col-resize shrink-0"
            :title="overlayExpanded ? 'Collapse' : 'Expand'"
          >
            <Maximize2 v-if="!overlayExpanded" class="w-3 h-3" />
            <Minimize2 v-else class="w-3 h-3" />
          </button>
          <!-- Content -->
          <div class="flex-1 flex flex-col min-h-0 pointer-events-auto">
            <router-view class="flex-1 min-h-0" />
          </div>
        </div>
      </transition>
    </main>
  </div>
</template>

<style scoped>
.overlay-slide-enter-active, .overlay-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.overlay-slide-enter-from, .overlay-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
