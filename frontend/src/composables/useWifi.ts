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
      const avail = data.available_networks || []
      
      if (data.saved_networks && data.saved_networks.length > 0) {
        savedNetworks.value = data.saved_networks.map((n: any) => {
          const matched = avail.find((a: any) => a.ssid === n.ssid)
          return {
            id: n.ssid,
            ssid: n.ssid,
            isSecure: n.is_secure !== undefined ? n.is_secure : n.isSecure,
            isConnected: n.isConnected,
            signal: n.isConnected ? (data.signal_strength || 100) : (matched ? matched.signal : 0)
          }
        })
      } else if (data.connected && data.ssid) {
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

      // Keep available networks updated from status broadcast if present
      if (data.available_networks && data.available_networks.length > 0) {
        const savedSsids = new Set(savedNetworks.value.map(s => s.ssid))
        availableNetworks.value = data.available_networks
          .filter((n: any) => !savedSsids.has(n.ssid))
          .map((n: any) => ({
            id: n.ssid,
            ssid: n.ssid,
            isSecure: n.isSecure !== undefined ? n.isSecure : !!n.is_secure,
            isConnected: false,
            signal: n.signal
          }))
      }
    } catch (e) {
      console.error('Errore fetch wifi status:', e)
    }
  }

  const scanNetworks = async () => {
    isScanning.value = true
    try {
      const data = await api.getWiFiNetworks()
      const savedSsids = new Set(savedNetworks.value.map(s => s.ssid))
      availableNetworks.value = data
        .filter((n: any) => !savedSsids.has(n.ssid))
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

  const forgetNetwork = async (ssid: string) => {
    try {
      await api.forgetWiFi(ssid)
      await fetchStatus()
    } catch (e) {
      console.error('Errore forget wifi connection:', e)
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
    disconnectWifi,
    forgetNetwork
  }
}
