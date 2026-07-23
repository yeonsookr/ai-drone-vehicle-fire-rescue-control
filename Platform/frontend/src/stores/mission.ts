import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { missionApi } from '@/lib/api/missions'
import type { Mission } from '@/types'

export const useMissionStore = defineStore('mission', () => {
  const missions = ref<Mission[]>([])
  const selectedId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const selected = computed(() => {
    if (!selectedId.value) return null
    return missions.value.find(m => m.id === selectedId.value) ?? null
  })

  async function fetch() {
    loading.value = true; error.value = null
    try {
      const { data } = await missionApi.list()
      missions.value = data
    } catch (e: any) {
      error.value = e.message ?? 'Failed to fetch missions'
    } finally { loading.value = false }
  }

  function select(id: string | null) { selectedId.value = id }

  return { missions, selectedId, loading, error, selected, fetch, select }
})
