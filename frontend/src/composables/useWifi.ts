import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

export interface WifiNetwork {
  id: string
  ssid: string
  isSecure: boolean
  isConnected: boolean
  signal: number
}

const savedNetworks = ref<WifiNetwork[]>([])
const availableNetworks = ref<WifiNetwork[]>([])
const isScanning = ref(false)

export function useWifi() {
  const currentSsid = computed(() => savedNetworks.value.find(n => n.isConnected)?.ssid || null)

  const fetchStatus = async () => {
    try {
      const data = await api.getWiFiStatus()
      if (data.connected && data.ssid) {
        savedNetworks.value = [{
          id: data.ssid,
          ssid: data.ssid,
          isSecure: true,
          isConnected: true,
          signal: data.signal_strength || 100
        }]
      } else {
        savedNetworks.value = []
      }
    } catch (e) {
      console.error('Errore fetch wifi status:', e)
    }
  }

  const scanNetworks = async () => {
    isScanning.value = true
    try {
      const data = await api.getWiFiNetworks()
      const activeSsid = currentSsid.value
      availableNetworks.value = data
        .filter((n: any) => n.ssid !== activeSsid)
        .map((n: any) => ({
          id: n.ssid,
          ssid: n.ssid,
          isSecure: n.isSecure,
          isConnected: false,
          signal: n.signal
        }))
    } catch (e) {
      console.error('Errore scan wifi:', e)
    } finally {
      isScanning.value = false
    }
  }

  const connectToWifi = async (ssid: string, password?: string) => {
    try {
      const data = await api.connectWiFi(ssid, password)
      if (data.success) {
        await fetchStatus()
      }
      return data.success
    } catch (e) {
      console.error('Errore connessione wifi:', e)
      return false
    }
  }

  const disconnectWifi = async () => {
    try {
      const data = await api.disconnectWiFi()
      if (data.success) {
        await fetchStatus()
      }
    } catch (e) {
      console.error('Errore disconnessione wifi:', e)
    }
  }

  onMounted(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  })

  return {
    savedNetworks,
    availableNetworks,
    isScanning,
    currentSsid,
    fetchStatus,
    scanNetworks,
    connectToWifi,
    disconnectWifi
  }
}
