import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

export interface BluetoothDevice {
  id: string
  name: string
  isConnected: boolean
  isFavorite: boolean
  isPaired: boolean
}

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
      const data = await api.getBluetoothStatus()
      if (data) {
        adapterName.value = data.device_name || 'MITO-fr'
        isPowered.value = data.connected || false
        
        const devices = (data.available_devices || []).map((d: any) => ({
          id: d.address,
          name: d.name || d.address,
          isConnected: d.isConnected,
          isFavorite: d.address === localStorage.getItem('bt_favorite'),
          isPaired: d.isPaired
        }))
        
        pairedDevices.value = devices.filter((d: any) => d.isPaired)
        availableDevices.value = devices.filter((d: any) => !d.isPaired)
      }
    } catch (e) {
      console.error('BT Status error:', e)
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
      const data = await api.getBluetoothDevices()
      const devices = data.map((d: any) => ({
        id: d.address,
        name: d.name || d.address,
        isConnected: d.isConnected,
        isFavorite: d.address === localStorage.getItem('bt_favorite'),
        isPaired: d.isPaired
      }))
      pairedDevices.value = devices.filter((d: any) => d.isPaired)
      availableDevices.value = devices.filter((d: any) => !d.isPaired)
    } catch (e) {
      console.error('Errore scan bluetooth:', e)
    } finally {
      isScanning.value = false
    }
  }

  const toggleConnection = async (id: string) => {
    const device = pairedDevices.value.find(d => d.id === id) || availableDevices.value.find(d => d.id === id)
    if (!device) return

    try {
      if (device.isConnected) {
        await api.disconnectBluetooth()
      } else {
        await api.connectBluetooth(id)
      }
      await fetchStatus()
    } catch (e) {
      console.error(`Errore connection bluetooth:`, e)
    }
  }

  const connectToFavorite = async () => {
    if (favoriteDevice.value && !favoriteDevice.value.isConnected) {
      await toggleConnection(favoriteDevice.value.id)
    }
  }

  const setDiscoverable = async (enabled: boolean) => {
    try {
      await api.setDiscoverable(enabled)
      isDiscoverable.value = enabled
      await fetchStatus()
    } catch (e) {
      console.error('Errore set discoverable:', e)
    }
  }

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
