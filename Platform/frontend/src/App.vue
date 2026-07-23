<script setup lang="ts">
import { computed, toRef } from 'vue'
import { useTelemetryService } from '@/services/telemetryService'
import { useUiStore } from '@/stores/ui'
import { useDrag } from '@/composables/useDrag'
import Sidebar from '@/components/Sidebar.vue'
import MapPanel from '@/components/MapPanel.vue'
import FloatingDetail from '@/components/FloatingDetail.vue'
import FloatingMissionDetail from '@/components/FloatingMissionDetail.vue'
import FloatingStream from '@/components/FloatingStream.vue'

const telemetry = useTelemetryService()
const ui = useUiStore()
const connected = computed(() => telemetry.connected)

const streamDrag = useDrag(toRef(ui, 'streamPos'))
const detailDrag = useDrag(toRef(ui, 'detailPos'))
const missionDrag = useDrag(toRef(ui, 'missionPos'))

function centerPos(pos: { x: number; y: number } | null): Record<string, string> {
  if (!pos) return {}
  return { left: '50%', top: '50%', transform: `translate(-50%, -50%) translate(${pos.x}px, ${pos.y}px)` }
}
function rightPos(pos: { x: number; y: number } | null): Record<string, string> {
  if (!pos) return {}
  return { right: '1rem', top: '50%', transform: `translate(0, -50%) translate(${pos.x}px, ${pos.y}px)` }
}

function onPointerMove(e: PointerEvent) {
  streamDrag.onMove(e)
  detailDrag.onMove(e)
  missionDrag.onMove(e)
}

function onPointerUp() {
  streamDrag.onRelease()
  detailDrag.onRelease()
  missionDrag.onRelease()
}
</script>

<template>
  <div
    class="flex h-screen bg-[#0f0f0f] text-gray-200"
    @click="ui.closeAll"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
  >
    <!-- Section 1: Sidebar + Content -->
    <div class="w-80 flex flex-col min-h-0 bg-[#1a1a1a] border-r border-gray-800" @click.stop>
      <div class="h-14 flex items-center justify-between px-4 border-b border-gray-800 shrink-0">
        <span class="text-[11px] font-bold tracking-widest text-gray-500 uppercase">AIoT CTRL</span>
        <span class="text-[10px]" :class="connected ? 'text-green-400' : 'text-red-400'">{{ connected ? '● Connected' : '○ Disconnected' }}</span>
      </div>
      <div class="shrink-0 border-b border-gray-800">
        <Sidebar />
      </div>
      <div class="flex-1 flex flex-col min-h-0">
        <router-view class="flex-1 min-h-0" />
      </div>
    </div>

    <!-- Map -->
    <main class="flex-1 relative min-h-0">
      <MapPanel class="absolute inset-0" />

      <!-- Section 2: Camera stream -->
      <div
        v-if="ui.streamId"
        class="absolute z-20"
        :class="ui.streamPos ? 'left-1/2 top-1/2' : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'"
        :style="centerPos(ui.streamPos)"
      >
        <FloatingStream :stream-id="ui.streamId" :on-grab="streamDrag.onGrab" @close="ui.closeStream()" @select="ui.openStream" />
      </div>

      <!-- Section 3: Detail overlays -->
      <div
        v-if="ui.detailDeviceId"
        class="absolute z-30 h-11/12"
        :class="ui.detailPos ? '' : 'top-4 right-4'"
        :style="rightPos(ui.detailPos)"
        @click.stop
      >
        <FloatingDetail :device-id="ui.detailDeviceId" :on-grab="detailDrag.onGrab" @close="ui.closeDetail()" />
      </div>
      <div
        v-if="ui.missionId"
        class="absolute z-30 h-11/12"
        :class="ui.missionPos ? '' : 'top-4 right-4'"
        :style="rightPos(ui.missionPos)"
        @click.stop
      >
        <FloatingMissionDetail :mission-id="ui.missionId" :on-grab="missionDrag.onGrab" @close="ui.closeMission()" />
      </div>
    </main>
  </div>
</template>
