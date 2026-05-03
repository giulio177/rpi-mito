<script setup lang="ts">
import { onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { useBluetoothStore } from '@/stores/bluetooth'
import { useWiFiStore } from '@/stores/wifi'
import wsManager from '@/services/websocket'
import MainLayout from '@/components/layout/MainLayout.vue'

const audioStore = useAudioStore()
const bluetoothStore = useBluetoothStore()
const wifiStore = useWiFiStore()

onMounted(async () => {
  wsManager.connect()
  await Promise.all([
    audioStore.fetchStatus(),
    bluetoothStore.fetchStatus(),
    wifiStore.fetchStatus(),
  ])
})
</script>

<template>
  <MainLayout />
</template>