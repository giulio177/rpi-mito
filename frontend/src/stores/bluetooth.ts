import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BluetoothStatus, BluetoothDevice } from '@/types'
import api from '@/services/api'

export const useBluetoothStore = defineStore('bluetooth', () => {
  const enabled = ref(false)
  const discovering = ref(false)
  const connectedDevice = ref<BluetoothDevice | null>(null)
  const devices = ref<BluetoothDevice[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const status = await api.getBluetoothStatus()
      enabled.value = status.enabled
      discovering.value = status.discovering
      connectedDevice.value = status.connected_device
      devices.value = status.devices
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch BT status'
    } finally {
      isLoading.value = false
    }
  }

  async function scanDevices(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const deviceList = await api.getBluetoothDevices()
      devices.value = deviceList
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to scan devices'
    } finally {
      isLoading.value = false
    }
  }

  async function connect(address: string): Promise<void> {
    error.value = null
    try {
      const result = await api.connectBluetooth(address)
      if (result.success) {
        await scanDevices()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to connect'
    }
  }

  async function disconnect(): Promise<void> {
    error.value = null
    try {
      const result = await api.disconnectBluetooth()
      if (result.success) {
        connectedDevice.value = null
        await scanDevices()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to disconnect'
    }
  }

  function updateFromWs(data: Partial<BluetoothStatus>): void {
    if (data.enabled !== undefined) {
      enabled.value = data.enabled
    }
    if (data.discovering !== undefined) {
      discovering.value = data.discovering
    }
    if (data.connected_device !== undefined) {
      connectedDevice.value = data.connected_device
    }
    if (data.devices !== undefined) {
      devices.value = data.devices
    }
  }

  return {
    enabled,
    discovering,
    connectedDevice,
    devices,
    isLoading,
    error,
    fetchStatus,
    scanDevices,
    connect,
    disconnect,
    updateFromWs,
  }
})