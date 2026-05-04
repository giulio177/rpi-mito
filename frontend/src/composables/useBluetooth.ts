import { ref, computed, onMounted } from 'vue'

export interface BluetoothDevice {
  id: string
  name: string
  isConnected: boolean
  isFavorite: boolean
  isPaired: boolean
}

const API_BASE = 'http://localhost:8000/api/bluetooth'

// Stato globale per mantenere la sincronizzazione tra i componenti
const pairedDevices = ref<BluetoothDevice[]>([])
const availableDevices = ref<BluetoothDevice[]>([])
const isScanning = ref(false)

export function useBluetooth() {
  const connectedDevice = computed(() => pairedDevices.value.find(d => d.isConnected))

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const data = await res.json()
      // Il backend ritorna paired_devices e connected_device_id
      pairedDevices.value = data.paired_devices.map((d: any) => ({
        ...d,
        isConnected: d.id === data.connected_device_id,
        isFavorite: false // Gestito localmente o nel backend se implementato
      }))
    } catch (e) {
      console.error('Errore fetch bluetooth status:', e)
    }
  }

  const scanDevices = async () => {
    isScanning.value = true
    try {
      const res = await fetch(`${API_BASE}/devices`)
      const data = await res.json()
      availableDevices.value = data.filter((d: any) => !d.isPaired)
    } catch (e) {
      console.error('Errore scan bluetooth:', e)
    } finally {
      isScanning.value = false
    }
  }

  const toggleConnection = async (id: string) => {
    const device = pairedDevices.value.find(d => d.id === id)
    if (!device) return

    const endpoint = device.isConnected ? 'disconnect' : 'connect'
    try {
      const res = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: id })
      })
      const data = await res.json()
      if (data.success) {
        await fetchStatus() // Rinfresca lo stato
      }
    } catch (e) {
      console.error(`Errore ${endpoint} bluetooth:`, e)
    }
  }

  // Polling leggero ogni 5 secondi per lo stato della connessione
  onMounted(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  })

  return { 
    pairedDevices, 
    availableDevices, 
    isScanning,
    connectedDevice, 
    fetchStatus, 
    scanDevices, 
    toggleConnection 
  }
}
