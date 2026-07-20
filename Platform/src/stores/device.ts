import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { droneApi } from '@/lib/api/drones'
import { gatewayApi } from '@/lib/api/gateways'
import type { Drone, Gateway } from '@/types'

export const useDeviceStore = defineStore('device', () => {
  const drones = ref<Drone[]>([])
  const gateways = ref<Gateway[]>([])
  const selectedDroneId = ref<string | null>(null)
  const selectedGatewayId = ref<string | null>(null)
  const loading = ref(false)

  const selectedDrone = computed(() =>
    drones.value.find((d) => d.id === selectedDroneId.value) ?? null
  )
  const selectedGateway = computed(() =>
    gateways.value.find((g) => g.id === selectedGatewayId.value) ?? null
  )

  async function fetchDrones() {
    loading.value = true
    try {
      const { data } = await droneApi.list()
      drones.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchGateways() {
    loading.value = true
    try {
      const { data } = await gatewayApi.list()
      gateways.value = data
    } finally {
      loading.value = false
    }
  }

  function selectDrone(id: string | null) {
    selectedDroneId.value = id
    selectedGatewayId.value = null
  }

  function selectGateway(id: string | null) {
    selectedGatewayId.value = id
    selectedDroneId.value = null
  }

  return {
    drones, gateways, selectedDroneId, selectedGatewayId,
    selectedDrone, selectedGateway, loading,
    fetchDrones, fetchGateways, selectDrone, selectGateway,
  }
})
