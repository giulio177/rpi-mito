import { ref, computed } from 'vue'

// Dati finti iniziali
const pairedDevices = ref([
  { id: 'bt1', name: 'iPhone di Marco', isConnected: true, isFavorite: true },
  { id: 'bt2', name: 'AirPods Pro', isConnected: false, isFavorite: false }
])

export function useBluetooth() {
  const connectedDevice = computed(() => pairedDevices.value.find(d => d.isConnected))
  const favoriteDevice = computed(() => pairedDevices.value.find(d => d.isFavorite))

  const toggleFavorite = (id: string) => {
    pairedDevices.value.forEach(d => {
      d.isFavorite = (d.id === id)
    })
  }

  const toggleConnection = (id: string) => {
    pairedDevices.value.forEach(d => {
      if (d.id === id) d.isConnected = !d.isConnected
      else d.isConnected = false // Disconnette gli altri
    })
  }
  
  const connectToFavorite = () => {
    if (favoriteDevice.value) {
      toggleConnection(favoriteDevice.value.id)
    }
  }

  return { pairedDevices, connectedDevice, favoriteDevice, toggleFavorite, toggleConnection, connectToFavorite }
}
