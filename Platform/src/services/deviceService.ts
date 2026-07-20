import { useDeviceStore } from '@/stores/device'

export function fetchDrones() {
  return useDeviceStore().fetchDrones()
}

export function fetchGateways() {
  return useDeviceStore().fetchGateways()
}
