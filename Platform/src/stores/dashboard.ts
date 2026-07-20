import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi } from '@/lib/api/dashboard'
import type { DashboardSummary } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  const summary = ref<DashboardSummary>({
    active_drones: 0,
    online_gateways: 0,
    active_vehicles: 0,
    streaming_count: 0,
    active_alerts: 0,
    active_missions: 0,
  })

  async function fetchSummary() {
    try {
      const { data } = await dashboardApi.summary()
      summary.value = data
    } catch {
      // mock 대비 — 에러 무시
    }
  }

  return { summary, fetchSummary }
})
