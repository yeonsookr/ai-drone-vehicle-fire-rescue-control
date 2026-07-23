<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { useStreamService } from '@/services/streamService'
import OverlayPanel from '@/components/OverlayPanel.vue'
import MediaFeed from '@/components/MediaFeed.vue'
import { useVideoStream } from '@/composables/useVideoStream'

const ui = useUiStore()
const streamSvc = useStreamService()
const video = useVideoStream()
</script>

<template>
  <div class="flex flex-col gap-4 h-full">
    <OverlayPanel>
      <div class="flex-1 grid grid-cols-2 auto-rows-min gap-2 content-start" style="min-height: 200px">
        <div
          v-for="s in streamSvc.all" :key="s.id"
          @click="ui.openStream(s.id)"
          class="aspect-video bg-gray-900/80 rounded border relative overflow-hidden min-w-24 cursor-pointer transition-colors hover:border-gray-400"
          :class="s.id === ui.streamId ? 'border-gray-300 border-2' : 'border-gray-700'"
        >
          <MediaFeed :src="video.getUrl(s.device_id)" class="absolute inset-0" />
          <span class="absolute top-1 left-1 z-10 bg-black/60 px-1 rounded text-[9px] text-gray-300">{{ s.device_id }}</span>
        </div>
      </div>
    </OverlayPanel>
  </div>
</template>
