<template>
  <div class="w-full h-full flex pt-6 px-8 gap-8 text-white min-h-0">
    
    <!-- Sidebar -->
    <div class="w-64 flex flex-col gap-2 pb-32 shrink-0">
      <h1 class="text-3xl font-semibold mb-6 px-4">Impostazioni</h1>
      
      <button 
        @click="activeTab = 'general'"
        class="w-full text-left px-4 py-4 rounded-2xl transition-colors font-medium text-lg"
        :class="activeTab === 'general' ? 'bg-[#ddb7ff]/20 text-[#ddb7ff]' : 'hover:bg-white/10 text-white'"
      >
        Generali
      </button>

      <button 
        @click="activeTab = 'wifi'"
        class="w-full text-left px-4 py-4 rounded-2xl transition-colors font-medium text-lg"
        :class="activeTab === 'wifi' ? 'bg-[#ddb7ff]/20 text-[#ddb7ff]' : 'hover:bg-white/10 text-white'"
      >
        Wi-Fi
      </button>

      <button 
        @click="activeTab = 'bluetooth'"
        class="w-full text-left px-4 py-4 rounded-2xl transition-colors font-medium text-lg"
        :class="activeTab === 'bluetooth' ? 'bg-[#ddb7ff]/20 text-[#ddb7ff]' : 'hover:bg-white/10 text-white'"
      >
        Bluetooth
      </button>
    </div>

    <!-- Divisore -->
    <div class="w-[1px] bg-white/10 shrink-0 my-4"></div>

    <!-- Content Area -->
    <div class="flex-1 flex flex-col min-h-0 relative">

      <!-- Overlay chiusura menu contestuale -->
      <div v-if="activeMenuId !== null" @click.stop="activeMenuId = null" class="fixed inset-0 z-40 bg-transparent"></div>

      <!-- GENERAL -->
      <div v-if="activeTab === 'general'" class="flex-1 flex items-center justify-center">
        <p class="text-white/40 text-lg">Impostazioni Generali...</p>
      </div>

      <!-- BLUETOOTH -->
      <div v-else-if="activeTab === 'bluetooth'" class="flex-1 flex flex-col min-h-0 relative">
        <!-- Header Fisso -->
        <div class="flex items-center justify-between mb-6 shrink-0 pt-2">
          <h2 class="text-3xl font-semibold">Bluetooth</h2>
          <div class="w-14 h-8 rounded-full bg-[#ddb7ff] p-1 cursor-pointer flex justify-end">
            <div class="w-6 h-6 rounded-full bg-white shadow-md"></div>
          </div>
        </div>

        <!-- Area Scrollabile Unica -->
        <div 
          class="flex-1 overflow-y-auto pb-40 pr-4 custom-scrollbar flex flex-col gap-6"
          style="-webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 5%, black 100%); mask-image: linear-gradient(to bottom, transparent 0%, black 5%, black 100%);"
        >
          <!-- Spacer inziale per via del mask -->
          <div class="h-2 shrink-0"></div>

          <!-- Discoverable Row -->
          <div @click="renameRaspberry" class="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-2xl shrink-0 cursor-pointer hover:bg-white/10 transition-colors">
            <div class="flex flex-col">
              <span class="text-lg font-medium">Visibile come "{{ raspberryName }}"</span>
              <span class="text-sm text-white/50">Dispositivi vicini possono rilevare questo sistema.</span>
            </div>
            <button class="w-10 h-10 rounded-full flex items-center justify-center bg-white/5 hover:bg-white/10 transition-colors text-white/70">
              <span class="material-symbols-outlined text-[20px]">edit</span>
            </button>
          </div>
          
          <!-- I tuoi dispositivi -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2">I tuoi dispositivi</h3>
            <div 
              v-for="(device, index) in pairedDevices" 
              :key="device.id"
              @click="toggleConnection(device.id)"
              class="flex items-center justify-between p-4 transition-colors rounded-2xl mb-2 cursor-pointer relative"
              :class="activeMenuId === device.id ? 'shadow-2xl bg-white/10' : 'bg-white/5 hover:bg-white/10'"
              :style="{ zIndex: activeMenuId === device.id ? 50 : 1 }"
            >
              <div class="flex flex-col">
                <div class="flex items-center">
                  <span class="text-lg font-medium text-white">{{ device.name }}</span>
                  <span v-if="device.isFavorite" class="material-symbols-outlined filled text-[#ddb7ff] text-sm ml-2">star</span>
                </div>
                <span v-if="device.isConnected" class="text-sm text-[#ddb7ff] font-medium mt-0.5">Connesso</span>
                <span v-else class="text-sm text-white/40 mt-0.5">Non connesso</span>
              </div>
              
              <div class="flex items-center relative">
                <button @click.stop="openMenu(device.id)" class="w-10 h-10 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
                  <span class="material-symbols-outlined text-white/70">more_vert</span>
                </button>

                <!-- Popover -->
                <div v-if="activeMenuId === device.id" 
                     @click.stop
                     :class="[
                       'absolute right-0 w-48 bg-[#1c1c1e]/90 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl p-2 flex flex-col gap-1 animate-in fade-in zoom-in-95 duration-200',
                       index >= pairedDevices.length - 1 ? 'bottom-12 origin-bottom-right' : 'top-12 origin-top-right'
                     ]"
                     style="z-index: 9999;"
                     >
                  <button v-if="!device.isFavorite" @click="toggleFavorite(device.id); activeMenuId = null" class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/10 text-[#ddb7ff] transition-colors text-left">
                    <span class="material-symbols-outlined text-[20px]">star</span>
                    <span class="font-medium text-sm">Imposta Preferito</span>
                  </button>
                  <div v-if="!device.isFavorite" class="h-[1px] w-full bg-white/10 my-0.5"></div>
                  <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/10 text-white transition-colors text-left">
                    <span class="material-symbols-outlined text-[18px]">edit</span>
                    <span class="font-medium text-sm">Rinomina</span>
                  </button>
                  <div class="h-[1px] w-full bg-white/10 my-0.5"></div>
                  <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors text-left">
                    <span class="material-symbols-outlined text-[18px]">delete</span>
                    <span class="font-medium text-sm">Dissocia</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Altri dispositivi -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2 mt-2">Altri dispositivi</h3>
            <div 
              v-for="device in availableDevices" 
              :key="device.id"
              class="flex items-center justify-between p-4 bg-white/5 hover:bg-white/10 transition-colors rounded-2xl mb-2 cursor-pointer"
            >
              <span class="text-lg font-medium text-white">{{ device.name }}</span>
            </div>
          </div>

        </div>
      </div>

      <!-- WI-FI -->
      <div v-else-if="activeTab === 'wifi'" class="flex-1 flex flex-col min-h-0 relative">
        <!-- Header Fisso -->
        <div class="flex items-center justify-between mb-6 shrink-0 pt-2">
          <h2 class="text-3xl font-semibold">Wi-Fi</h2>
          <div class="w-14 h-8 rounded-full bg-[#ddb7ff] p-1 cursor-pointer flex justify-end">
            <div class="w-6 h-6 rounded-full bg-white shadow-md"></div>
          </div>
        </div>

        <!-- Area Scrollabile Unica -->
        <div 
          class="flex-1 overflow-y-auto pb-40 pr-4 custom-scrollbar flex flex-col gap-6"
          style="-webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 5%, black 100%); mask-image: linear-gradient(to bottom, transparent 0%, black 5%, black 100%);"
        >
          <!-- Spacer inziale per via del mask -->
          <div class="h-2 shrink-0"></div>

          <!-- Reti Salvate -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2">Reti Salvate</h3>
            <div 
              v-for="(net, index) in savedNetworks" 
              :key="net.id"
              @click="toggleWifi(net)"
              class="flex items-center justify-between p-4 transition-colors rounded-2xl mb-2 cursor-pointer relative"
              :class="activeMenuId === net.id ? 'shadow-2xl bg-white/10' : 'bg-white/5 hover:bg-white/10'"
              :style="{ zIndex: activeMenuId === net.id ? 50 : 1 }"
            >
              <div class="flex items-center gap-3">
                <span v-if="net.isSecure" class="material-symbols-outlined text-white/50 text-[20px]">lock</span>
                <div class="flex flex-col">
                  <span class="text-lg font-medium text-white">{{ net.ssid }}</span>
                  <span v-if="net.isConnected" class="text-sm text-[#ddb7ff] font-medium mt-0.5">Connesso</span>
                </div>
              </div>
              
              <div class="flex items-center relative">
                <button @click.stop="openMenu(net.id)" class="w-10 h-10 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
                  <span class="material-symbols-outlined text-white/70">more_vert</span>
                </button>

                <!-- Popover -->
                <div v-if="activeMenuId === net.id" 
                     @click.stop
                     :class="[
                       'absolute right-0 w-48 bg-[#1c1c1e]/90 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl p-2 flex flex-col gap-1 animate-in fade-in zoom-in-95 duration-200',
                       index >= savedNetworks.length - 1 ? 'bottom-12 origin-bottom-right' : 'top-12 origin-top-right'
                     ]"
                     style="z-index: 9999;"
                     >
                  <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors text-left">
                    <span class="material-symbols-outlined text-[18px]">delete</span>
                    <span class="font-medium text-sm">Elimina rete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Altre Reti -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2 mt-2">Altre Reti</h3>
            <div 
              v-for="net in availableNetworks" 
              :key="net.id"
              @click="connectToNewWifi(net)"
              class="flex items-center justify-between p-4 bg-white/5 hover:bg-white/10 transition-colors rounded-2xl mb-2 cursor-pointer"
            >
              <div class="flex items-center gap-3">
                <span v-if="net.isSecure" class="material-symbols-outlined text-white/50 text-[20px]">lock</span>
                <span class="text-lg font-medium text-white">{{ net.ssid }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useBluetooth } from '@/composables/useBluetooth'
import { useKeyboard } from '@/composables/useKeyboard'

const route = useRoute()
const activeTab = ref(route.query.tab ? String(route.query.tab) : 'general')

watch(() => route.query.tab, (newTab) => {
  if (newTab) activeTab.value = String(newTab)
})

const activeMenuId = ref<number | string | null>(null)

const openMenu = (id: number | string) => {
  activeMenuId.value = activeMenuId.value === id ? null : id
}

// --- RASPBERRY NAME ---
const { openKeyboard } = useKeyboard()
const raspberryName = ref('Raspberry Pi')

const renameRaspberry = async () => {
  const newName = await openKeyboard(raspberryName.value, 'Rinomina Dispositivo')
  if (newName !== null && newName.trim() !== '') {
    raspberryName.value = newName.trim()
  }
}

// --- BLUETOOTH DATA ---
const { pairedDevices, toggleConnection, toggleFavorite } = useBluetooth()

const availableDevices = ref([
  { id: 'bt3', name: 'MacBook Pro', isConnected: false },
  { id: 'bt4', name: 'Unknown Device', isConnected: false },
])

// --- WI-FI DATA ---
const savedNetworks = ref([
  { id: 'wf1', ssid: 'Home-Net', isSecure: true, isConnected: true },
  { id: 'wf2', ssid: 'Office-5G', isSecure: true, isConnected: false },
])

const availableNetworks = ref([
  { id: 'wf3', ssid: 'Starbucks WiFi', isSecure: false, isConnected: false },
  { id: 'wf4', ssid: 'Guest Network', isSecure: true, isConnected: false },
])

const toggleWifi = (net: any) => {
  if (!net.isConnected) {
    savedNetworks.value.forEach(n => n.isConnected = false)
  }
  net.isConnected = !net.isConnected
}

const connectToNewWifi = (net: any) => {
  if (net.isSecure) {
    alert(`Inserisci password per ${net.ssid}`)
  } else {
    alert(`Connessione a ${net.ssid} in corso...`)
  }
}
</script>