import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { missionApi } from '@/lib/api/missions'
import { commandApi } from '@/lib/api/commands'
import type { Mission, MissionLog, Command } from '@/types'

export const useMissionStore = defineStore('mission', () => {
  const missions = ref<Mission[]>([])
  const logs = ref<MissionLog[]>([])
  const commands = ref<Command[]>([])
  const selectedId = ref<string | null>(null)
  const loading = ref(false)
  const actionLoading = ref(false)
  const error = ref<string | null>(null)

  const selected = computed(() => {
    if (!selectedId.value) return null
    return missions.value.find(m => m.id === selectedId.value) ?? null
  })

  const selectedLogs = computed(() => {
    if (!selectedId.value) return []
    return logs.value.filter(l => l.mission_id === selectedId.value)
  })

  const selectedCommands = computed(() => {
    if (!selectedId.value) return []
    return commands.value.filter(c => c.mission_id === selectedId.value)
  })

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      const { data } = await missionApi.list()
      missions.value = data
    } catch (e: any) {
      error.value = e.message ?? 'Failed to fetch missions'
    } finally {
      loading.value = false
    }
  }

  function select(id: string | null) {
    selectedId.value = id
    if (id) {
      fetchLogs(id)
      fetchCommands(id)
    } else {
      logs.value = []
      commands.value = []
    }
  }

  async function fetchLogs(id: string) {
    try {
      const { data } = await missionApi.logs(id)
      logs.value = data
    } catch { /* ignore */ }
  }

  async function fetchCommands(id: string) {
    try {
      const { data } = await commandApi.list(id)
      commands.value = data
    } catch { /* ignore */ }
  }

  function applyUpdate(id: string, updated: Mission) {
    const idx = missions.value.findIndex(m => m.id === id)
    if (idx !== -1) missions.value[idx] = updated
  }

  async function start(id: string) {
    actionLoading.value = true
    error.value = null
    try {
      const { data } = await missionApi.start(id)
      applyUpdate(id, data)
      fetchLogs(id)
    } catch (e: any) {
      error.value = e.message ?? 'Failed to start mission'
      throw e
    } finally {
      actionLoading.value = false
    }
  }

  async function pause(id: string) {
    actionLoading.value = true
    error.value = null
    try {
      const { data } = await missionApi.pause(id)
      applyUpdate(id, data)
      fetchLogs(id)
    } catch (e: any) {
      error.value = e.message ?? 'Failed to pause mission'
      throw e
    } finally {
      actionLoading.value = false
    }
  }

  async function resume(id: string) {
    actionLoading.value = true
    error.value = null
    try {
      const { data } = await missionApi.resume(id)
      applyUpdate(id, data)
      fetchLogs(id)
    } catch (e: any) {
      error.value = e.message ?? 'Failed to resume mission'
      throw e
    } finally {
      actionLoading.value = false
    }
  }

  async function cancel(id: string) {
    actionLoading.value = true
    error.value = null
    try {
      const { data } = await missionApi.cancel(id)
      applyUpdate(id, data)
      fetchLogs(id)
    } catch (e: any) {
      error.value = e.message ?? 'Failed to cancel mission'
      throw e
    } finally {
      actionLoading.value = false
    }
  }

  return {
    missions, logs, commands, selectedId, loading, actionLoading, error,
    selected, selectedLogs, selectedCommands,
    fetch, select, start, pause, resume, cancel,
  }
})
