<template>
  <div class="flex-none h-10 z-50 flex justify-between items-center px-4 relative">
    
    <!-- Ora e Temperatura -->
    <div class="text-[#cfc2d6] font-medium tracking-wide">
      10:42 PM | 22°C
    </div>

    <!-- Area Status (Cliccabile) -->
    <button 
      class="flex items-center gap-3 text-[#cfc2d6] bg-white/5 border border-white/10 rounded-full px-4 py-1.5 transition-all outline-none focus:outline-none active:scale-95 active:bg-white/10 cursor-pointer"
      @click="showControlCenter = !showControlCenter"
    >
      <span class="material-symbols-outlined text-[20px]">wifi</span>
      <span class="material-symbols-outlined text-[20px]">bluetooth</span>
      <img :src="battery100" class="h-5 opacity-80" alt="Battery" />
    </button>

    <!-- Overlay Invisibile per chiusura -->
    <div 
      v-if="showControlCenter" 
      class="fixed inset-0 z-40" 
      @click="showControlCenter = false"
    ></div>

    <!-- Control Center Modale -->
    <div 
      v-if="showControlCenter"
      class="absolute top-14 right-4 z-50 w-72 bg-[#1c1c1e]/40 backdrop-blur-3xl border border-white/10 rounded-3xl p-4 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col gap-4 text-white"
    >
      <!-- Wi-Fi -->
      <button class="bg-white/5 hover:bg-white/10 border border-white/5 transition-colors rounded-2xl p-3 flex items-center gap-4 text-left">
        <div class="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-blue-400">wifi</span>
        </div>
        <div class="flex flex-col flex-1 min-w-0">
          <span class="font-semibold text-[15px]">Wi-Fi</span>
          <span class="text-[13px] text-white/50 truncate">Home-Net</span>
        </div>
      </button>

      <!-- Bluetooth -->
      <button class="bg-white/5 hover:bg-white/10 border border-white/5 transition-colors rounded-2xl p-3 flex items-center gap-4 text-left">
        <div class="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-blue-400">bluetooth</span>
        </div>
        <div class="flex flex-col flex-1 min-w-0">
          <span class="font-semibold text-[15px]">Bluetooth</span>
          <span class="text-[13px] text-white/50 truncate">iPhone di Marco</span>
        </div>
      </button>

      <!-- Settings Button -->
      <button 
        @click="goToSettings"
        class="mt-2 py-3 px-4 rounded-xl bg-white/5 hover:bg-white/10 text-center font-medium text-sm transition-colors text-white/80"
      >
        Tutte le impostazioni
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import battery100 from '@/assets/battery/battery.100percent.svg'

const router = useRouter()
const showControlCenter = ref(false)

const goToSettings = () => {
  showControlCenter.value = false
  router.push('/settings')
}
// In futuro qui collegheremo i WebSocket per l'ora e i sensori
</script>