import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BluetoothStatus } from '@/types'
import api from '@/services/api'

export const useBluetoothStore = defineStore('bluetooth', () => {
  const connected = ref(false)
  const deviceName = ref<string | null>(null)
  const deviceAddress = ref<string | null>(null)
  const batteryLevel = ref<number | null>(null)
  const availableDevices = ref<any[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const status = await api.getBluetoothStatus()
      connected.value = status.connected
      deviceName.value = status.device_name
      deviceAddress.value = status.device_address
      batteryLevel.value = status.battery_level
      availableDevices.value = status.available_devices
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
      availableDevices.value = deviceList
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
        await fetchStatus()
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
        connected.value = false
        deviceName.value = null
        deviceAddress.value = null
        batteryLevel.value = null
        await fetchStatus()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to disconnect'
    }
  }

  function updateFromWs(data: Partial<BluetoothStatus>): void {
    if (data.connected !== undefined) {
      connected.value = data.connected
    }
    if (data.device_name !== undefined) {
      deviceName.value = data.device_name
    }
    if (data.device_address !== undefined) {
      deviceAddress.value = data.device_address
    }
    if (data.battery_level !== undefined) {
      batteryLevel.value = data.battery_level
    }
    if (data.available_devices !== undefined) {
      availableDevices.value = data.available_devices
    }
  }

  return {
    connected,
    deviceName,
    deviceAddress,
    batteryLevel,
    availableDevices,
    isLoading,
    error,
    fetchStatus,
    scanDevices,
    connect,
    disconnect,
    updateFromWs,
  }
})