<template>
  <div class="flex-none h-20 z-10 w-full">
    <div class="w-[90%] mx-auto h-full rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 flex justify-between items-center px-6 shadow-[0_0_20px_rgba(168,85,247,0.1)]">
      
      <!-- Left Tabs -->
      <div class="flex gap-2">
        <button
          v-for="item in navItems"
          :key="item.path"
          @click="router.push(item.path)"
          class="transition-all duration-200 ease-out active:scale-90"
          :class="route.path === item.path 
            ? 'bg-[#ddb7ff]/20 text-[#ddb7ff] rounded-2xl w-16 h-14 shadow-[0_0_15px_rgba(221,183,255,0.2)] flex flex-col items-center justify-center' 
            : 'text-white/40 w-16 h-14 hover:text-white hover:bg-white/5 rounded-2xl flex flex-col items-center justify-center'"
        >
          <span class="material-symbols-outlined" :class="{ 'filled': route.path === item.path }">{{ item.icon }}</span>
        </button>
      </div>

      <!-- Right Audio Controls -->
      <div class="flex items-center gap-4 bg-black/20 rounded-full px-4 py-2 border border-white/5">
        <span @click="volume = Math.max(0, volume - 10)" class="material-symbols-outlined text-white/40 text-[20px] cursor-pointer hover:text-white transition-all duration-200 active:scale-75">volume_mute</span>
        <div class="relative w-32 h-1 bg-white/10 rounded-full">
          <!-- Parte Riempita -->
          <div class="absolute top-0 left-0 h-full bg-[#ddb7ff] rounded-full shadow-[0_0_10px_rgba(221,183,255,0.8)] pointer-events-none" :style="{ width: volume + '%' }"></div>
          <!-- Input Range Invisibile Interattivo -->
          <input type="range" min="0" max="100" v-model="volume" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer m-0 z-10" />
        </div>
        <span @click="volume = Math.min(100, volume + 10)" class="material-symbols-outlined text-[#ddb7ff] text-[20px] cursor-pointer hover:brightness-125 transition-all duration-200 active:scale-75">volume_up</span>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const volume = ref(60)

const navItems = [
  { path: '/', icon: 'home' },
  { path: '/music', icon: 'music_note' },
  { path: '/obd', icon: 'speed' },
  { path: '/maps', icon: 'map' },
  { path: '/settings', icon: 'settings' }
]
</script>