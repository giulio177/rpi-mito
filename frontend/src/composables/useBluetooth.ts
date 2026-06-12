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
        
        const rememberedAddrs = JSON.parse(localStorage.getItem('bt_remembered') || '[]') as string[]
        let updatedRemembered = [...rememberedAddrs]
        let changed = false

        const devices = (data.available_devices || []).map((d: any) => {
          const isConnected = d.isConnected === true
          const isPaired = d.isPaired === true || rememberedAddrs.includes(d.address)
          
          if (isConnected && !updatedRemembered.includes(d.address)) {
            updatedRemembered.push(d.address)
            changed = true
          }

          return {
            id: d.address,
            name: d.name || d.address,
            isConnected,
            isFavorite: d.address === localStorage.getItem('bt_favorite'),
            isPaired
          }
        })

        if (changed) {
          localStorage.setItem('bt_remembered', JSON.stringify(updatedRemembered))
        }
        
        pairedDevices.value = devices.filter((d: any) => d.isPaired)
        availableDevices.value = devices.filter((d: any) => !d.isPaired)
      }
    } catch (e) {
      console.error('BT Status error:', e)
    }
  }

  const toggleFavorite = (id: string) => {
    const currentFav = localStorage.getItem('bt_favorite')
    if (currentFav === id) {
      localStorage.removeItem('bt_favorite')
    } else {
      localStorage.setItem('bt_favorite', id)
    }
    pairedDevices.value.forEach(d => {
      d.isFavorite = (d.id === id && currentFav !== id)
    })
  }

  const scanDevices = async () => {
    isScanning.value = true
    try {
      const data = await api.getBluetoothDevices()
      const rememberedAddrs = JSON.parse(localStorage.getItem('bt_remembered') || '[]') as string[]
      let updatedRemembered = [...rememberedAddrs]
      let changed = false

      const devices = data.map((d: any) => {
        const isConnected = d.isConnected === true
        const isPaired = d.isPaired === true || rememberedAddrs.includes(d.address)

        if (isConnected && !updatedRemembered.includes(d.address)) {
          updatedRemembered.push(d.address)
          changed = true
        }

        return {
          id: d.address,
          name: d.name || d.address,
          isConnected,
          isFavorite: d.address === localStorage.getItem('bt_favorite'),
          isPaired
        }
      })

      if (changed) {
        localStorage.setItem('bt_remembered', JSON.stringify(updatedRemembered))
      }

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
        device.isConnected = false
        await api.disconnectBluetooth()
      } else {
        await api.connectBluetooth(id)
      }
      await fetchStatus()
    } catch (e) {
      console.error(`Errore connection bluetooth:`, e)
    }
  }

  const forgetDevice = async (id: string) => {
    try {
      await api.unpairBluetooth(id)
      
      const rememberedAddrs = JSON.parse(localStorage.getItem('bt_remembered') || '[]') as string[]
      const updatedRemembered = rememberedAddrs.filter(addr => addr !== id)
      localStorage.setItem('bt_remembered', JSON.stringify(updatedRemembered))

      if (localStorage.getItem('bt_favorite') === id) {
        localStorage.removeItem('bt_favorite')
      }
      await fetchStatus()
    } catch (e) {
      console.error('Errore forget device:', e)
    }
  }

  const disconnectDevice = async () => {
    try {
      pairedDevices.value.forEach(d => { d.isConnected = false })
      availableDevices.value.forEach(d => { d.isConnected = false })
      await api.disconnectBluetooth()
      await fetchStatus()
    } catch (e) {
      console.error('Errore disconnect device:', e)
    }
  }

  const connectToFavorite = async () => {
    if (connectedDevice.value) {
      await toggleConnection(connectedDevice.value.id)
    } else if (favoriteDevice.value) {
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
    forgetDevice,
    disconnectDevice,
    setDiscoverable
  }
}
