<script setup lang="ts">
import { ref } from 'vue'
import { CameraOff } from '@lucide/vue'

defineProps<{ src: string; alt?: string }>()
const errored = ref(false)
</script>

<template>
  <div class="relative w-full h-full bg-gray-900 overflow-hidden">
    <!-- Error / offline fallback -->
    <div v-if="errored" class="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-500">
      <CameraOff class="w-8 h-8" />
      <span class="text-xs">Feed unavailable</span>
    </div>
    <!-- Live image / MJPEG stream (hidden on error) -->
    <img
      v-show="!errored"
      :src="src"
      :alt="alt ?? 'Live feed'"
      class="w-full h-full object-cover"
      @error="errored = true"
    />
  </div>
</template>
