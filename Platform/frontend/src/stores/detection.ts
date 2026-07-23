import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { detectionApi } from '@/lib/api/detections'
import type { AiDetection, OperatorJudgment } from '@/types'

export const useDetectionStore = defineStore('detection', () => {
  const events = ref<AiDetection[]>([])
  const selectedId = ref<string | null>(null)
  const loading = ref(false)

  const selected = computed(() =>
    events.value.find((e) => e.id === selectedId.value) ?? null
  )

  const unconfirmed = computed(() =>
    events.value.filter((e) => e.operator_judgment === 'unconfirmed')
  )

  const alertCount = computed(() => unconfirmed.value.length)

  async function fetch() {
    loading.value = true
    try {
      const { data } = await detectionApi.list()
      events.value = data
    } finally {
      loading.value = false
    }
  }

  function select(id: string | null) {
    selectedId.value = id
  }

  async function judge(id: string, judgment: OperatorJudgment, _reason?: string) {
    // IoTServer has POST /api/detections/snapshot (edge upload), not judge.
    // Judge will be implemented when detection query API is available.
    const idx = events.value.findIndex((e) => e.id === id)
    if (idx !== -1) events.value[idx] = { ...events.value[idx], operator_judgment: judgment }
  }

  return {
    events, selectedId, loading, selected, unconfirmed, alertCount,
    fetch, select, judge,
  }
})
