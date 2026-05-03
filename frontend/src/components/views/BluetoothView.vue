<script setup lang="ts">
import { useBluetoothStore } from '@/stores/bluetooth'
const bluetoothStore = useBluetoothStore()
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-semibold">Bluetooth</h2>
      <span :class="bluetoothStore.enabled ? 'text-green-400' : 'text-red-400'">
        {{ bluetoothStore.enabled ? 'Attivo' : 'Disattivo' }}
      </span>
    </div>
    <div v-if="bluetoothStore.connectedDevice" class="mb-6 p-4 bg-green-900/30 rounded-lg">
      <p class="text-green-400 font-semibold">Connesso a:</p>
      <p class="text-xl">{{ bluetoothStore.connectedDevice.name }}</p>
      <button
        @click="bluetoothStore.disconnect()"
        class="mt-2 px-4 py-2 bg-red-600 rounded-lg"
      >
        Disconnetti
      </button>
    </div>
    <div class="flex-1 overflow-auto">
      <h3 class="text-lg font-semibold mb-3">Dispositivi disponibili</h3>
      <div v-if="bluetoothStore.devices.length === 0" class="text-gray-400">
        Nessun dispositivo trovato
      </div>
      <div
        v-for="device in bluetoothStore.devices"
        :key="device.address"
        class="flex justify-between items-center p-4 bg-gray-800 rounded-lg mb-2"
      >
        <div>
          <p class="font-semibold">{{ device.name }}</p>
          <p class="text-gray-400 text-sm">{{ device.address }}</p>
        </div>
        <button
          v-if="!device.connected"
          @click="bluetoothStore.connect(device.address)"
          class="px-4 py-2 bg-blue-600 rounded-lg"
        >
          Connetti
        </button>
      </div>
    </div>
  </div>
</template>