import { ref, computed, onMounted } from 'vue'

export interface WifiNetwork {
  id: string
  ssid: string
  isSecure: boolean
  isConnected: boolean
  signal: number
}

const API_BASE = 'http://localhost:8000/api/wifi'

const savedNetworks = ref<WifiNetwork[]>([])
const availableNetworks = ref<WifiNetwork[]>([])
const isScanning = ref(false)

export function useWifi() {
  const currentSsid = computed(() => savedNetworks.value.find(n => n.isConnected)?.ssid || null)

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const data = await res.json()
      // Il backend ritorna un oggetto con is_enabled, current_ssid, networks (salvate)
      savedNetworks.value = data.networks.map((n: any) => ({
        ...n,
        id: n.ssid,
        isConnected: n.ssid === data.current_ssid
      }))
    } catch (e) {
      console.error('Errore fetch wifi status:', e)
    }
  }

  const scanNetworks = async () => {
    isScanning.value = true
    try {
      const res = await fetch(`${API_BASE}/networks`)
      const data = await res.json()
      // Filtriamo quelle non salvate o le separiamo
      availableNetworks.value = data.filter((n: any) => 
        !savedNetworks.value.find(sn => sn.ssid === n.ssid)
      ).map((n: any) => ({ ...n, id: n.ssid, isConnected: false }))
    } catch (e) {
      console.error('Errore scan wifi:', e)
    } finally {
      isScanning.value = false
    }
  }

  const connectToWifi = async (ssid: string, password?: string) => {
    try {
      const res = await fetch(`${API_BASE}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ssid, password })
      })
      const data = await res.json()
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
      const res = await fetch(`${API_BASE}/disconnect`, { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        await fetchStatus()
      }
    } catch (e) {
      console.error('Errore disconnessione wifi:', e)
    }
  }

  onMounted(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 10000) // Polling più lento per il WiFi
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
