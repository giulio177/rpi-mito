import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WiFiStatus, WiFiNetwork } from '@/types'
import api from '@/services/api'

export const useWiFiStore = defineStore('wifi', () => {
  const enabled = ref(false)
  const connected = ref(false)
  const currentSsid = ref<string | null>(null)
  const ipAddress = ref<string | null>(null)
  const networks = ref<WiFiNetwork[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const status = await api.getWiFiStatus()
      enabled.value = status.enabled
      connected.value = status.connected
      currentSsid.value = status.current_ssid
      ipAddress.value = status.ip_address
      networks.value = status.networks
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
      networks.value = networkList
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to scan networks'
    } finally {
      isLoading.value = false
    }
  }

  async function connect(ssid: string, password?: string): Promise<void> {
    error.value = null
    try {
      const result = await api.connectWiFi(ssid, password)
      if (result.success) {
        await scanNetworks()
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
        currentSsid.value = null
        ipAddress.value = null
        await scanNetworks()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to disconnect'
    }
  }

  function updateFromWs(data: Partial<WiFiStatus>): void {
    if (data.enabled !== undefined) {
      enabled.value = data.enabled
    }
    if (data.connected !== undefined) {
      connected.value = data.connected
    }
    if (data.current_ssid !== undefined) {
      currentSsid.value = data.current_ssid
    }
    if (data.ip_address !== undefined) {
      ipAddress.value = data.ip_address
    }
    if (data.networks !== undefined) {
      networks.value = data.networks
    }
  }

  return {
    enabled,
    connected,
    currentSsid,
    ipAddress,
    networks,
    isLoading,
    error,
    fetchStatus,
    scanNetworks,
    connect,
    disconnect,
    updateFromWs,
  }
})