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
          class="aspect-video bg-gray-900/80 rounded border border-gray-700 flex items-center justify-center text-xs text-gray-600 relative overflow-hidden min-w-24 cursor-pointer transition-colors hover:border-gray-500"
        >
          <MediaFeed :src="video.getUrl(s.device_id)" class="absolute inset-0" />
          <span class="relative z-10 bg-black/40 px-1 rounded text-[10px]">{{ s.device_id }}</span>
        </div>
      </div>
    </OverlayPanel>
  </div>
</template>
