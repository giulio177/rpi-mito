<script setup lang="ts">
import { useWiFiStore } from '@/stores/wifi'
const wifiStore = useWiFiStore()
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-semibold">WiFi</h2>
      <span :class="wifiStore.enabled ? 'text-green-400' : 'text-red-400'">
        {{ wifiStore.enabled ? 'Attivo' : 'Disattivo' }}
      </span>
    </div>
    <div v-if="wifiStore.connected" class="mb-6 p-4 bg-green-900/30 rounded-lg">
      <p class="text-green-400 font-semibold">Connesso a:</p>
      <p class="text-xl">{{ wifiStore.currentSsid }}</p>
      <p class="text-gray-400 text-sm">{{ wifiStore.ipAddress }}</p>
      <button
        @click="wifiStore.disconnect()"
        class="mt-2 px-4 py-2 bg-red-600 rounded-lg"
      >
        Disconnetti
      </button>
    </div>
    <div class="flex-1 overflow-auto">
      <h3 class="text-lg font-semibold mb-3">Reti disponibili</h3>
      <div v-if="wifiStore.networks.length === 0" class="text-gray-400">
        Nessuna rete trovata
      </div>
      <div
        v-for="network in wifiStore.networks"
        :key="network.ssid"
        class="flex justify-between items-center p-4 bg-gray-800 rounded-lg mb-2"
      >
        <div>
          <p class="font-semibold">{{ network.ssid }}</p>
          <p class="text-gray-400 text-sm">Segnale: {{ network.signal }}%</p>
        </div>
        <span v-if="network.connected" class="text-green-400">✓</span>
      </div>
    </div>
  </div>
</template>