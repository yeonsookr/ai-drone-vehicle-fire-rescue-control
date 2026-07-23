import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // ── Floating overlay state (survives navigation) ──
  const detailDeviceId = ref<string | null>(null)
  const missionId = ref<string | null>(null)
  const streamId = ref<number | null>(null)

  function openDetail(id: string) { detailDeviceId.value = id }
  function closeDetail() { detailDeviceId.value = null }
  function toggleDetail(id: string) {
    detailDeviceId.value = detailDeviceId.value === id ? null : id
  }

  function openMission(id: string) { missionId.value = id }
  function closeMission() { missionId.value = null }
  function toggleMission(id: string) {
    missionId.value = missionId.value === id ? null : id
  }

  function openStream(id: number) { streamId.value = id }
  function closeStream() { streamId.value = null }

  function closeAll() {
    detailDeviceId.value = null
    missionId.value = null
    streamId.value = null
  }

  return {
    detailDeviceId, missionId, streamId,
    openDetail, closeDetail, toggleDetail,
    openMission, closeMission, toggleMission,
    openStream, closeStream,
    closeAll,
  }
})
