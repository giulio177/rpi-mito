import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WiFiStatus } from '@/types'
import api from '@/services/api'

export const useWiFiStore = defineStore('wifi', () => {
  const connected = ref(false)
  const ssid = ref<string | null>(null)
  const ipAddress = ref<string | null>(null)
  const signalStrength = ref(0)
  const availableNetworks = ref<any[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const status = await api.getWiFiStatus()
      connected.value = status.connected
      ssid.value = status.ssid
      ipAddress.value = status.ip_address
      signalStrength.value = status.signal_strength
      availableNetworks.value = status.available_networks
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch WiFi status'
    } finally {
      isLoading.value = false
    }
  }

  async function scanNetworks(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const networkList = await api.getWiFiNetworks()
      availableNetworks.value = networkList
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to scan networks'
    } finally {
      isLoading.value = false
    }
  }

  async function connect(ssidVal: string, password?: string): Promise<void> {
    error.value = null
    try {
      const result = await api.connectWiFi(ssidVal, password)
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
      const result = await api.disconnectWiFi()
      if (result.success) {
        connected.value = false
        ssid.value = null
        ipAddress.value = null
        signalStrength.value = 0
        await fetchStatus()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to disconnect'
    }
  }

  function updateFromWs(data: Partial<WiFiStatus>): void {
    if (data.connected !== undefined) {
      connected.value = data.connected
    }
    if (data.ssid !== undefined) {
      ssid.value = data.ssid
    }
    if (data.ip_address !== undefined) {
      ipAddress.value = data.ip_address
    }
    if (data.signal_strength !== undefined) {
      signalStrength.value = data.signal_strength
    }
    if (data.available_networks !== undefined) {
      availableNetworks.value = data.available_networks
    }
  }

  return {
    connected,
    ssid,
    ipAddress,
    signalStrength,
    availableNetworks,
    isLoading,
    error,
    fetchStatus,
    scanNetworks,
    connect,
    disconnect,
    updateFromWs,
  }
})