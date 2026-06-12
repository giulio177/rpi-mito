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
      <div v-if="activeTab === 'general'" class="flex-1 flex flex-col gap-6 overflow-y-auto pb-40 pr-4 pt-2">

        <!-- Info & Aggiornamento -->
        <div class="bg-white/5 border border-white/10 p-6 rounded-3xl flex flex-col gap-5">
          <div>
            <h2 class="text-2xl font-semibold mb-1">Sistema</h2>
            <p class="text-white/40 text-sm">Informazioni sulla versione e aggiornamenti OTA</p>
          </div>

          <div class="flex items-center justify-between bg-white/5 rounded-2xl px-5 py-4">
            <div>
              <p class="text-sm text-white/50 font-medium uppercase tracking-wider mb-0.5">Versione</p>
              <p class="text-white font-semibold text-lg">{{ systemVersion }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-white/50 font-medium uppercase tracking-wider mb-0.5">Branch</p>
              <p class="text-white/70 font-medium font-mono">{{ systemBranch }} · {{ systemCommit }}</p>
            </div>
          </div>

          <button
            id="btn-system-update"
            @click="handleUpdate"
            :disabled="isUpdating"
            class="flex items-center justify-center gap-3 bg-[#ddb7ff] text-black font-bold px-6 py-3.5 rounded-xl transition-all active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span v-if="isUpdating" class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
            <span v-else class="material-symbols-outlined text-[20px]">cloud_download</span>
            <span>{{ isUpdating ? 'Aggiornamento in corso...' : 'Cerca Aggiornamenti (Pull da GitHub)' }}</span>
          </button>

          <!-- Feedback aggiornamento -->
          <div v-if="updateLog" class="rounded-xl px-4 py-3 text-sm font-mono bg-white/5 border border-white/10 text-white/50 whitespace-pre-wrap">
            {{ updateLog }}
          </div>
        </div>

        <!-- Alimentazione (Danger zone) -->
        <div class="bg-red-500/5 border border-red-500/20 p-6 rounded-3xl flex flex-col gap-4">
          <div>
            <h2 class="text-2xl font-semibold mb-1">Alimentazione</h2>
            <p class="text-white/40 text-sm">Operazioni di riavvio e spegnimento del sistema</p>
          </div>

          <!-- Riavvia solo app -->
          <button
            id="btn-reboot-app"
            @click="handleRebootApp"
            :disabled="isPowerBusy"
            class="w-full flex items-center gap-4 px-5 py-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all active:scale-[0.98] disabled:opacity-60 text-left"
          >
            <span class="material-symbols-outlined text-white/70 text-[24px]">refresh</span>
            <div>
              <p class="font-semibold text-white">Riavvia Solo App</p>
              <p class="text-sm text-white/40">Ricarica il kiosk senza riavviare il Pi</p>
            </div>
          </button>

          <!-- Riavvia sistema -->
          <button
            id="btn-reboot-system"
            @click="triggerAction('reboot')"
            :disabled="isPowerBusy"
            class="w-full flex items-center gap-4 px-5 py-4 rounded-2xl bg-white/5 hover:bg-orange-500/10 border border-white/10 hover:border-orange-500/30 transition-all active:scale-[0.98] disabled:opacity-60 text-left"
          >
            <span class="material-symbols-outlined text-orange-400 text-[24px]">restart_alt</span>
            <div>
              <p class="font-semibold text-orange-300">Riavvia Sistema</p>
              <p class="text-sm text-white/40">Spegne e riavvia il Raspberry Pi</p>
            </div>
          </button>

          <!-- Spegni -->
          <button
            id="btn-shutdown"
            @click="triggerAction('shutdown')"
            :disabled="isPowerBusy"
            class="w-full flex items-center gap-4 px-5 py-4 rounded-2xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 hover:border-red-500/40 transition-all active:scale-[0.98] disabled:opacity-60 text-left"
          >
            <span class="material-symbols-outlined text-red-400 text-[24px]">power_settings_new</span>
            <div>
              <p class="font-semibold text-red-400">Spegni Raspberry Pi</p>
              <p class="text-sm text-white/40">Spegnimento completo del sistema</p>
            </div>
          </button>
        </div>

      </div>

      <!-- BLUETOOTH -->
      <div v-else-if="activeTab === 'bluetooth'" class="flex-1 flex flex-col min-h-0 relative">
        <!-- Header Fisso -->
        <div class="flex items-center justify-between mb-6 shrink-0 pt-2">
          <h2 class="text-3xl font-semibold">Bluetooth</h2>
          <div class="flex items-center gap-3">
            <span class="text-sm font-medium text-white/50">{{ isDiscoverable ? 'Visibile' : 'Nascosto' }}</span>
            <div 
              @click="handleToggleDiscoverable"
              class="w-14 h-8 rounded-full p-1 cursor-pointer transition-colors duration-300"
              :class="isDiscoverable ? 'bg-[#ddb7ff] justify-end' : 'bg-white/10 justify-start'"
              style="display: flex; align-items: center;"
            >
              <div class="w-6 h-6 rounded-full bg-white shadow-md"></div>
            </div>
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
            <div class="flex items-center justify-between mb-4 pl-2">
              <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider">I tuoi dispositivi</h3>
              <button @click="scanBluetooth" :disabled="isScanningBt" class="text-xs font-bold text-[#ddb7ff] uppercase hover:opacity-80 disabled:opacity-50">
                {{ isScanningBt ? 'Scansione...' : 'Aggiorna' }}
              </button>
            </div>
            
            <div v-if="pairedDevices.length === 0" class="p-8 text-center bg-white/5 rounded-2xl border border-dashed border-white/10 text-white/30">
              Nessun dispositivo associato
            </div>

            <div 
              v-for="(device, index) in pairedDevices" 
              :key="device.id"
              @click="toggleBluetoothConnection(device.id)"
              class="flex items-center justify-between p-4 transition-colors rounded-2xl mb-2 cursor-pointer relative"
              :class="activeMenuId === device.id ? 'shadow-2xl bg-white/10' : 'bg-white/5 hover:bg-white/10'"
              :style="{ zIndex: activeMenuId === device.id ? 50 : 1 }"
            >
              <div class="flex flex-col">
                <div class="flex items-center">
                  <span class="text-lg font-medium text-white">{{ device.name || 'Dispositivo Sconosciuto' }}</span>
                  <span v-if="device.isFavorite" class="material-symbols-outlined filled text-[#ddb7ff] text-sm ml-2">star</span>
                </div>
                <span v-if="device.isConnected" class="text-sm text-[#ddb7ff] font-medium mt-0.5">Connesso</span>
                <span v-else class="text-sm text-white/40 mt-0.5">Disponibile</span>
              </div>
              
              <div class="flex items-center relative">
                <button @click.stop="openMenu(device.id)" class="w-10 h-10 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
                  <span class="material-symbols-outlined text-white/70">more_vert</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Altri dispositivi -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2 mt-2">Dispositivi Rilevati</h3>
            <div 
              v-for="device in availableDevices" 
              :key="device.id"
              @click="toggleBluetoothConnection(device.id)"
              class="flex items-center justify-between p-4 bg-white/5 hover:bg-white/10 transition-colors rounded-2xl mb-2 cursor-pointer"
            >
              <span class="text-lg font-medium text-white">{{ device.name || device.id }}</span>
              <span class="material-symbols-outlined text-white/30">add_circle</span>
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
            <div class="flex items-center justify-between mb-4 pl-2">
              <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider">Reti Conosciute</h3>
              <button @click="scanWifi" :disabled="isScanningWifi" class="text-xs font-bold text-[#ddb7ff] uppercase hover:opacity-80 disabled:opacity-50">
                {{ isScanningWifi ? 'Ricerca...' : 'Cerca Reti' }}
              </button>
            </div>
            <div v-if="savedNetworks.length === 0" class="p-8 text-center bg-white/5 rounded-2xl border border-dashed border-white/10 text-white/30">
              Nessuna rete Wi-Fi salvata
            </div>
            <div 
              v-for="(net, index) in savedNetworks" 
              :key="net.id"
              @click="handleWifiConnect(net)"
              class="flex items-center justify-between p-4 transition-colors rounded-2xl mb-2 cursor-pointer relative"
              :class="activeMenuId === net.id ? 'shadow-2xl bg-white/10' : 'bg-white/5 hover:bg-white/10'"
              :style="{ zIndex: activeMenuId === net.id ? 50 : 1 }"
            >
              <div class="flex items-center gap-3">
                <span v-if="net.isSecure" class="material-symbols-outlined text-white/50 text-[20px]">lock</span>
                <div class="flex flex-col">
                  <span class="text-lg font-medium text-white">{{ net.ssid }}</span>
                  <span v-if="net.isConnected" class="text-sm text-[#ddb7ff] font-medium mt-0.5">Connesso</span>
                  <span v-else class="text-sm text-white/40 mt-0.5">Salvata</span>
                </div>
              </div>
              
              <div class="flex items-center relative">
                <button @click.stop="openMenu(net.id)" class="w-10 h-10 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
                  <span class="material-symbols-outlined text-white/70">more_vert</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Altre Reti -->
          <div class="shrink-0">
            <h3 class="text-sm font-bold text-white/50 uppercase tracking-wider mb-4 pl-2 mt-2">Reti Disponibili</h3>
            <div 
              v-for="net in availableNetworks" 
              :key="net.id"
              @click="handleWifiConnect(net)"
              class="flex items-center justify-between p-4 bg-white/5 hover:bg-white/10 transition-colors rounded-2xl mb-2 cursor-pointer"
            >
              <div class="flex items-center gap-3">
                <span v-if="net.isSecure" class="material-symbols-outlined text-white/50 text-[20px]">lock</span>
                <span class="text-lg font-medium text-white">{{ net.ssid }}</span>
              </div>
              <span class="text-xs text-white/30 font-mono">{{ net.signal }}%</span>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>

  <!-- MODAL DI AGGIORNAMENTO PRONTO -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="showUpdateModal" class="fixed inset-0 z-[9999] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-md" @click="showUpdateModal = false"></div>
        <div class="relative bg-[#1c1c1e] border border-white/10 w-[500px] rounded-[40px] p-8 shadow-2xl flex flex-col gap-6 animate-in zoom-in-95 duration-300">
          <div class="w-20 h-20 bg-[#ddb7ff]/20 rounded-full flex items-center justify-center mx-auto">
            <span class="material-symbols-outlined text-[#ddb7ff] text-4xl">system_update</span>
          </div>
          <div class="text-center">
            <h3 class="text-2xl font-bold text-white mb-2">Aggiornamento Pronto</h3>
            <p class="text-white/60">
              Il nuovo codice è stato scaricato. Per applicare le modifiche è necessario riavviare:
              <span v-if="updateManifest.restart_backend" class="block font-bold text-[#ddb7ff] mt-2">• Servizi Backend</span>
              <span v-if="updateManifest.restart_kiosk" class="block font-bold text-[#ddb7ff]">• Interfaccia Grafica</span>
            </p>
          </div>
          <div class="flex flex-col gap-3">
            <button @click="applyUpdateRestarts" class="w-full py-4 bg-[#ddb7ff] text-[#490080] font-bold rounded-2xl active:scale-95 transition-transform">
              Riavvia e Applica
            </button>
            <button @click="showUpdateModal = false" class="w-full py-4 bg-white/5 text-white/50 font-medium rounded-2xl">
              Più tardi
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- MODAL DI CONFERMA -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="showConfirmModal" class="fixed inset-0 z-[9999] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showConfirmModal = false"></div>
        <div class="relative bg-[#1c1c1e] border border-white/10 rounded-3xl p-8 w-80 flex flex-col gap-6 shadow-2xl">
          <div class="flex flex-col items-center gap-3 text-center">
            <span class="material-symbols-outlined text-[48px]"
                  :class="pendingAction === 'shutdown' ? 'text-red-400' : 'text-orange-400'">
              {{ pendingAction === 'shutdown' ? 'power_settings_new' : 'restart_alt' }}
            </span>
            <h3 class="text-xl font-bold">
              {{ isUpdateReboot ? 'Aggiornamento completato' : 'Sei sicuro?' }}
            </h3>
            <p class="text-white/50 text-sm">
              <span v-if="pendingAction === 'shutdown'">
                Stai per spegnere il Raspberry Pi. Dovrai riaccenderlo manualmente.
              </span>
              <span v-else-if="isUpdateReboot">
                Aggiornamento completato con successo. Per applicare le modifiche è necessario riavviare il sistema. Vuoi riavviare ora?
              </span>
              <span v-else>
                Stai per riavviare il sistema. L'interfaccia sarà temporaneamente non disponibile.
              </span>
            </p>
          </div>
          <div class="flex gap-3">
            <button @click="closeConfirmModal"
              class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20 font-semibold transition-colors">
              Annulla
            </button>
            <button @click="executePendingAction"
              class="flex-1 py-3 rounded-xl font-bold transition-colors"
              :class="pendingAction === 'shutdown' ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-orange-500 hover:bg-orange-600 text-white'">
              Conferma
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- MODALE NOTIFICA / ERRORE -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="alertMessage" class="fixed inset-0 z-[9999] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="alertMessage = ''"></div>
        <div class="relative bg-[#1c1c1e] border border-white/10 rounded-[30px] p-8 w-80 flex flex-col gap-6 shadow-2xl items-center text-center">
          <span class="material-symbols-outlined text-[48px] text-[#ddb7ff]">info</span>
          <h3 class="text-xl font-bold">Notifica</h3>
          <p class="text-white/70 text-sm">{{ alertMessage }}</p>
          <button @click="alertMessage = ''" class="w-full py-3 rounded-xl bg-[#ddb7ff] text-[#490080] font-bold active:scale-95 transition-transform">
            OK
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- MODALE CONFERMA DISCONNESSIONE WIFI -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="wifiDisconnectPending" class="fixed inset-0 z-[9999] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="wifiDisconnectPending = null"></div>
        <div class="relative bg-[#1c1c1e] border border-white/10 rounded-[30px] p-8 w-80 flex flex-col gap-6 shadow-2xl items-center text-center">
          <span class="material-symbols-outlined text-[48px] text-orange-400">wifi_off</span>
          <h3 class="text-xl font-bold">Disconnetti</h3>
          <p class="text-white/50 text-sm">Sei sicuro di disconnetterti da {{ wifiDisconnectPending.ssid }}?</p>
          <div class="flex gap-3 w-full">
            <button @click="wifiDisconnectPending = null" class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20 font-semibold transition-colors">
              Annulla
            </button>
            <button @click="confirmWifiDisconnect" class="flex-1 py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold transition-colors">
              Conferma
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- MODAL DI RIAVVIO IN CORSO -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="showRebootingModal" class="fixed inset-0 z-[10000] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-xl"></div>
        <div class="relative bg-[#1c1c1e] border border-white/10 w-[450px] rounded-[40px] p-8 shadow-2xl flex flex-col gap-6 items-center text-center">
          <div class="w-20 h-20 bg-orange-500/20 rounded-full flex items-center justify-center animate-pulse">
            <span class="material-symbols-outlined text-orange-400 text-4xl">restart_alt</span>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-white mb-2">Aggiornamento completato</h3>
            <p class="text-white/60">
              Il codice è stato aggiornato ed il sistema si sta riavviando per applicare le modifiche.
            </p>
            <p class="text-white/40 text-sm mt-4">
              L'interfaccia si ricaricherà automaticamente tra pochi secondi.
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useBluetooth } from '@/composables/useBluetooth'
import { useWifi } from '@/composables/useWifi'
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

// --- BLUETOOTH ---
const { 
  pairedDevices, 
  availableDevices, 
  isScanning: isScanningBt, 
  scanDevices: scanBluetooth,
  toggleConnection: toggleBluetoothConnection,
  setDiscoverable
} = useBluetooth()

const isDiscoverable = ref(false)
const handleToggleDiscoverable = async () => {
  isDiscoverable.value = !isDiscoverable.value
  await setDiscoverable(isDiscoverable.value)
  if (isDiscoverable.value) {
    setTimeout(() => { isDiscoverable.value = false }, 60000)
  }
}

// --- WI-FI ---
const {
  savedNetworks,
  availableNetworks,
  isScanning: isScanningWifi,
  scanNetworks: scanWifi,
  connectToWifi,
  disconnectWifi
} = useWifi()

const alertMessage = ref('')
const wifiDisconnectPending = ref<any | null>(null)

const confirmWifiDisconnect = async () => {
  if (wifiDisconnectPending.value) {
    await disconnectWifi()
    wifiDisconnectPending.value = null
  }
}

const handleWifiConnect = async (net: any) => {
  if (net.isConnected) {
    wifiDisconnectPending.value = net
    return
  }

  let password = ''
  if (net.isSecure) {
    const res = await openKeyboard('', `Password per ${net.ssid}`)
    if (res === null) return 
    password = res
  }

  const success = await connectToWifi(net.ssid, password)
  if (!success) {
    alertMessage.value = 'Connessione fallita. Controlla la password.'
  }
}


// ─── SYSTEM ───────────────────────────────────────────────────────────────────

const API = 'http://localhost:8000'

const systemVersion = ref('v1.0')
const systemCommit  = ref('...')
const systemBranch  = ref('...')
const isUpdating    = ref(false)
const isPowerBusy   = ref(false)
const updateLog     = ref('')

// Modal di conferma generico
const showConfirmModal = ref(false)
const pendingAction = ref<'reboot' | 'shutdown' | null>(null)
const isUpdateReboot = ref(false)

// Modal di aggiornamento (Manifesto)
const showUpdateModal = ref(false)
const updateManifest = ref({ restart_backend: false, restart_kiosk: false })
const showRebootingModal = ref(false)

onMounted(async () => {
  try {
    const res = await fetch(`${API}/api/system/version`)
    const data = await res.json()
    systemVersion.value = data.version ? `v${data.version}` : 'v1.0'
    systemCommit.value  = data.commit?.substring(0, 7) || 'N/D'
    systemBranch.value  = data.branch || 'main'
  } catch (e) {}
})

const handleUpdate = async () => {
  isUpdating.value = true
  updateLog.value = 'Scarico ultimi aggiornamenti da GitHub (git pull)...'
  try {
    // Phase 1: Pull and check if there are changes
    const resPull = await fetch(`${API}/api/system/update/pull`, { method: 'POST' })
    const dataPull = await resPull.json()
    
    if (!dataPull.success) {
      updateLog.value = '✕ Errore nello scaricamento: ' + dataPull.message
      isUpdating.value = false
      return
    }
    
    if (!dataPull.changed) {
      updateLog.value = '✓ Codice già aggiornato. Nessuna installazione richiesta.'
      isUpdating.value = false
      return
    }
    
    // Phase 2: Run install script since code changed
    updateLog.value = '✓ Codice scaricato. Esecuzione dello script di installazione (questo potrebbe richiedere qualche minuto)...'
    const resInstall = await fetch(`${API}/api/system/update/install`, { method: 'POST' })
    const dataInstall = await resInstall.json()
    
    if (!dataInstall.success) {
      updateLog.value = '✕ Errore nell\'installazione: ' + dataInstall.message
      isUpdating.value = false
      return
    }
    
    updateLog.value = '✓ Installazione completata con successo. Riavvio richiesto.'
    
    // Open the confirmation reboot modal
    isUpdateReboot.value = true
    pendingAction.value = 'reboot'
    showConfirmModal.value = true
    
  } catch (e) {
    updateLog.value = '✕ Errore di connessione al sistema durante l\'aggiornamento.'
  } finally {
    isUpdating.value = false
  }
}

const applyUpdateRestarts = async () => {
  showUpdateModal.value = false
  isPowerBusy.value = true
  try {
    await fetch(`${API}/api/system/reboot-app`, { method: 'POST' })
  } catch (e) {}
}

const triggerAction = (action: 'reboot' | 'shutdown') => {
  pendingAction.value = action
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  showConfirmModal.value = false
  isUpdateReboot.value = false
}

const executePendingAction = async () => {
  const isReboot = pendingAction.value === 'reboot'
  showConfirmModal.value = false
  isPowerBusy.value = true
  const wasUpdateReboot = isUpdateReboot.value
  isUpdateReboot.value = false // reset flag
  try {
    const endpoint = pendingAction.value === 'shutdown'
      ? `${API}/api/system/shutdown`
      : `${API}/api/system/reboot`
    
    if (isReboot) {
      showRebootingModal.value = true
    }
    
    await fetch(endpoint, { method: 'POST' })
  } finally {
    isPowerBusy.value = false
    pendingAction.value = null
  }
}

const handleRebootApp = async () => {
  isPowerBusy.value = true
  try {
    await fetch(`${API}/api/system/reboot-app`, { method: 'POST' })
  } finally {
    isPowerBusy.value = false
  }
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>