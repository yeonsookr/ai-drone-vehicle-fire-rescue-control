import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface OverlayPos { x: number; y: number }

export const useUiStore = defineStore('ui', () => {
  // ── Overlay visibility ──
  const detailDeviceId = ref<string | null>(null)
  const missionId = ref<string | null>(null)
  const streamId = ref<number | null>(null)

  // ── Overlay positions (null = default CSS position) ──
  const detailPos = ref<OverlayPos | null>(null)
  const missionPos = ref<OverlayPos | null>(null)
  const streamPos = ref<OverlayPos | null>(null)

  function openDetail(id: string) { detailDeviceId.value = id }
  function closeDetail() { detailDeviceId.value = null; detailPos.value = null }
  function toggleDetail(id: string) {
    detailDeviceId.value = detailDeviceId.value === id ? null : id
  }

  function openMission(id: string) { missionId.value = id }
  function closeMission() { missionId.value = null; missionPos.value = null }
  function toggleMission(id: string) {
    missionId.value = missionId.value === id ? null : id
  }

  function openStream(id: number) { streamId.value = id }
  function closeStream() { streamId.value = null; streamPos.value = null }
  function closeAll() {
    detailDeviceId.value = null; detailPos.value = null
    missionId.value = null; missionPos.value = null
    streamId.value = null; streamPos.value = null
  }

  return {
    detailDeviceId, missionId, streamId,
    detailPos, missionPos, streamPos,
    openDetail, closeDetail, toggleDetail,
    openMission, closeMission, toggleMission,
    openStream, closeStream,
    closeAll,
  }
})
