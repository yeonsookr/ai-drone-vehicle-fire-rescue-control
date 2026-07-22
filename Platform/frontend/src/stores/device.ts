import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { droneApi } from '@/lib/api/drones'
import { vehicleApi } from '@/lib/api/vehicles'
import { gatewayApi } from '@/lib/api/gateways'
import type { Drone, Vehicle, Gateway } from '@/types'

export const useDeviceStore = defineStore('device', () => {
  const drones = ref<Drone[]>([])
  const vehicles = ref<Vehicle[]>([])
  const gateways = ref<Gateway[]>([])
  const selectedDroneId = ref<string | null>(null)
  const selectedVehicleId = ref<string | null>(null)
  const selectedGatewayId = ref<string | null>(null)
  const loading = ref(false)

  const selectedDrone = computed(() =>
    drones.value.find((d) => d.id === selectedDroneId.value) ?? null
  )
  const selectedVehicle = computed(() =>
    vehicles.value.find((v) => v.id === selectedVehicleId.value) ?? null
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

  async function fetchVehicles() {
    loading.value = true
    try {
      const { data } = await vehicleApi.list()
      vehicles.value = data
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
    selectedVehicleId.value = null
    selectedGatewayId.value = null
  }

  function selectVehicle(id: string | null) {
    selectedVehicleId.value = id
    selectedDroneId.value = null
    selectedGatewayId.value = null
  }

  function selectGateway(id: string | null) {
    selectedGatewayId.value = id
    selectedDroneId.value = null
    selectedVehicleId.value = null
  }

  return {
    drones, vehicles, gateways,
    selectedDroneId, selectedVehicleId, selectedGatewayId,
    selectedDrone, selectedVehicle, selectedGateway, loading,
    fetchDrones, fetchVehicles, fetchGateways,
    selectDrone, selectVehicle, selectGateway,
  }
})
