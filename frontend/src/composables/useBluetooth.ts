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
const adapterName = ref('MITO-fr')
const isPowered = ref(false)
const isDiscoverable = ref(false)

export function useBluetooth() {
  const connectedDevice = computed(() => pairedDevices.value.find(d => d.isConnected))
  const favoriteDevice = computed(() => pairedDevices.value.find(d => d.isFavorite) || pairedDevices.value[0])

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const data = await res.json()
      if (data) {
        adapterName.value = data.adapter_name || 'MITO-fr'
        isPowered.value = data.is_powered
        isDiscoverable.value = data.is_discoverable
        
        pairedDevices.value = (data.paired_devices || []).map((d: any) => ({
          ...d,
          isConnected: d.id === data.connected_device_id,
          isFavorite: d.id === localStorage.getItem('bt_favorite')
        }))
      }
    } catch (e) {
      console.error('BT Status error:', e)
    }
  }

  const fetchPairedDevices = async () => {
    try {
      const res = await fetch(`${API_BASE}/paired`)
      const data = await res.json()
      pairedDevices.value = data
    } catch (e) {
      console.error('Error fetching paired devices:', e)
    }
  }

  const toggleFavorite = (id: string) => {
    localStorage.setItem('bt_favorite', id)
    pairedDevices.value.forEach(d => {
      d.isFavorite = (d.id === id)
    })
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
    const device = pairedDevices.value.find(d => d.id === id) || availableDevices.value.find(d => d.id === id)
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
        await fetchStatus()
      }
    } catch (e) {
      console.error(`Errore ${endpoint} bluetooth:`, e)
    }
  }

  const connectToFavorite = async () => {
    if (favoriteDevice.value && !favoriteDevice.value.isConnected) {
      await toggleConnection(favoriteDevice.value.id)
    }
  }

  const setDiscoverable = async (enabled: boolean) => {
    try {
      await fetch(`${API_BASE}/discoverable?enabled=${enabled}`, { method: 'POST' })
      await fetchStatus()
    } catch (e) {
      console.error('Errore set discoverable:', e)
    }
  }

  // Polling leggero ogni 5 secondi per lo stato della connessione
  onMounted(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  })

  return { 
    adapterName,
    isPowered,
    isDiscoverable,
    pairedDevices, 
    availableDevices, 
    isScanning,
    connectedDevice, 
    favoriteDevice,
    fetchStatus, 
    scanDevices, 
    toggleConnection,
    toggleFavorite,
    connectToFavorite,
    setDiscoverable
  }
}
