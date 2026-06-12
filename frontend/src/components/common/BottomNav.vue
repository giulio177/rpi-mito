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
        <span 
          @mousedown="startMuteTimer"
          @mouseup="clearMuteTimer"
          @mouseleave="clearMuteTimer"
          @touchstart.passive="startMuteTimer"
          @touchend="clearMuteTimer"
          @touchcancel="clearMuteTimer"
          @click="handleVolumeDown"
          class="material-symbols-outlined text-[20px] cursor-pointer transition-all duration-200 active:scale-75 select-none"
          :class="muted ? 'text-red-400 hover:text-red-300 animate-pulse' : 'text-white/40 hover:text-white'"
        >
          {{ muted ? 'volume_off' : 'volume_mute' }}
        </span>
        <div class="relative w-64 h-2 bg-white/10 rounded-full">
          <!-- Parte Riempita -->
          <div 
            class="absolute top-0 left-0 h-full rounded-full pointer-events-none" 
            :class="[
              muted ? 'bg-white/20 shadow-none' : 'bg-[#ddb7ff] shadow-[0_0_10px_rgba(221,183,255,0.8)]',
              isDragging ? 'transition-none' : 'transition-all duration-200'
            ]" 
            :style="{ width: localVolume + '%' }"
          ></div>
          <!-- Input Range Invisibile Interattivo -->
          <input 
            type="range" 
            min="0" 
            max="100" 
            v-model="localVolume" 
            @input="onVolumeInput"
            @change="onDragEnd"
            @mousedown="onDragStart"
            @touchstart="onDragStart"
            @touchend="onDragEnd"
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer m-0 z-10" 
          />
        </div>
        <span @click="handleVolumeUp" class="material-symbols-outlined text-[#ddb7ff] text-[20px] cursor-pointer hover:brightness-125 transition-all duration-200 active:scale-75 select-none">volume_up</span>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()

const audioStore = useAudioStore()
const { volume, muted } = storeToRefs(audioStore)

const localVolume = ref(volume.value)
const isDragging = ref(false)

// Sync localVolume with store volume when not dragging
watch(volume, (newVal) => {
  if (!isDragging.value) {
    localVolume.value = newVal
  }
}, { immediate: true })

let lastCallTime = 0
let throttleTimer: any = null

const updateVolumeBackend = async (value: number) => {
  await audioStore.setVolume(value)
}

const throttledUpdateVolume = (value: number) => {
  const now = Date.now()
  const limit = 100 // update volume at most once every 100ms
  
  if (now - lastCallTime >= limit) {
    updateVolumeBackend(value)
    lastCallTime = now
  } else {
    if (throttleTimer) clearTimeout(throttleTimer)
    throttleTimer = setTimeout(() => {
      updateVolumeBackend(value)
      lastCallTime = Date.now()
    }, limit - (now - lastCallTime))
  }
}

const onVolumeInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const value = Number(target.value)
  localVolume.value = value
  throttledUpdateVolume(value)
}

const onDragStart = () => {
  isDragging.value = true
}

const onDragEnd = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const value = Number(target.value)
  localVolume.value = value
  
  if (throttleTimer) {
    clearTimeout(throttleTimer)
    throttleTimer = null
  }
  
  // Final, absolute sync on drag release
  await updateVolumeBackend(value)
  
  setTimeout(() => {
    isDragging.value = false
  }, 200)
}

// Mute long-press detection logic
const longPressTimer = ref<any>(null)
const wasLongPressed = ref(false)

const startMuteTimer = () => {
  wasLongPressed.value = false
  longPressTimer.value = setTimeout(async () => {
    wasLongPressed.value = true
    await audioStore.setMuted(!muted.value)
  }, 2000) // 2 seconds long press
}

const clearMuteTimer = () => {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

const handleVolumeDown = async () => {
  if (wasLongPressed.value) {
    wasLongPressed.value = false
    return
  }
  const newVol = Math.max(0, volume.value - 10)
  localVolume.value = newVol
  await audioStore.setVolume(newVol)
}

const handleVolumeUp = async () => {
  const newVol = Math.min(100, volume.value + 10)
  localVolume.value = newVol
  await audioStore.setVolume(newVol)
}

const navItems = [
  { path: '/', icon: 'home' },
  { path: '/music', icon: 'music_note' },
  { path: '/obd', icon: 'speed' },
  { path: '/maps', icon: 'map' },
  { path: '/settings', icon: 'settings' }
]
</script>
