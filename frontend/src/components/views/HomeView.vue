<template>
  <div class="flex-1 mt-4 mb-4 pb-28 z-10 grid grid-cols-12 gap-[24px] h-full min-h-0">
    
    <!-- Left Panel: Media Player -->
    <div @click="router.push('/music')" class="col-span-7 rounded-3xl overflow-hidden relative bg-white/5 backdrop-blur-2xl border border-white/10 group cursor-pointer transition-all hover:border-white/20">
      <div class="absolute inset-0 bg-cover bg-center brightness-50 mix-blend-overlay group-hover:scale-105 transition-transform duration-1000 ease-out" :style="{ backgroundImage: `url(${currentCover})` }"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-[#0e0e0e]/80 via-transparent to-[#0e0e0e]/30"></div>
      <div class="relative h-full flex flex-col justify-between p-[32px] z-10">
        <div>
          <h2 class="font-display-lg text-[48px] font-semibold leading-[1.1] tracking-[-0.02em] text-[#e2e2e2] mb-2 line-clamp-1">{{ currentTitle }}</h2>
          <p class="font-title-sm text-[20px] font-semibold leading-[1.4] text-[#ddb7ff]">{{ currentArtist }}</p>
        </div>
        <div class="flex flex-col gap-6" @click.stop>
          <div class="w-full flex items-center gap-4">
            <span class="text-[#cfc2d6] text-sm font-medium w-12 text-right">{{ currentTimeText }}</span>
            <div class="relative flex-1 h-1.5 bg-white/20 rounded-full">
              <!-- Parte Riempita -->
              <div class="absolute top-0 left-0 h-full bg-[#ddb7ff] rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)] pointer-events-none" :style="{ width: progressPercent + '%' }"></div>
              <!-- Input Range Invisibile Interattivo -->
              <input type="range" min="0" max="100" v-model.number="progressPercent" @input="handleSeek" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer m-0 z-10" />
            </div>
            <span class="text-[#cfc2d6] text-sm font-medium w-12 text-left">{{ remainingTimeText }}</span>
          </div>
          <div class="flex justify-center items-center gap-8">
            <button @click="handlePrev" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
              <span class="material-symbols-outlined text-[28px] text-[#e2e2e2]">skip_previous</span>
            </button>
            <button @click="togglePlay" class="w-[72px] h-[72px] flex items-center justify-center rounded-[24px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)]">
              <span class="material-symbols-outlined filled text-[40px]">{{ isPlaying ? 'pause' : 'play_arrow' }}</span>
            </button>
            <button @click="handleNext" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
              <span class="material-symbols-outlined text-[28px] text-[#e2e2e2]">skip_next</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Area: OBD & BT -->
    <div class="col-span-5 flex flex-col gap-[24px] h-full">
      <!-- OBD Panel -->
      <div @click="router.push('/obd')" class="flex-1 rounded-3xl bg-white/5 hover:bg-white/10 transition-colors backdrop-blur-2xl border border-white/10 flex flex-row justify-around items-center p-6 relative overflow-hidden cursor-pointer group">
        <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-[#ddb7ff]/20 rounded-full blur-[40px] z-0"></div>
        <div class="absolute -left-10 -top-10 w-40 h-40 bg-blue-500/10 rounded-full blur-[40px] z-0"></div>
        <div class="flex flex-col items-center justify-center z-10">
          <div class="flex items-baseline gap-1">
            <span class="font-display-lg text-[80px] leading-none font-light tracking-tighter text-[#e2e2e2]">120</span>
          </div>
          <span class="font-label-caps text-[12px] font-bold tracking-widest text-[#ddb7ff] mt-2">KM/H</span>
        </div>
        <div class="w-[1px] h-2/3 bg-white/10 z-10"></div>
        <div class="flex flex-col items-center justify-center z-10">
          <div class="flex items-baseline gap-1">
            <span class="font-display-lg text-[64px] leading-none font-light tracking-tighter text-[#cfc2d6]">3.5</span>
          </div>
          <span class="font-label-caps text-[12px] font-bold tracking-widest text-[#cfc2d6] mt-2">RPM x1000</span>
        </div>
      </div>

      <!-- BT Panel -->
      <button 
        @click="connectToFavorite"
        class="h-24 w-full rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 flex items-center px-6 gap-5 text-left transition-all hover:bg-white/10 active:scale-[0.98] cursor-pointer"
      >
        <div class="w-12 h-12 rounded-full flex items-center justify-center transition-colors border shrink-0"
             :class="connectedDevice ? 'bg-[#ddb7ff]/20 border-[#ddb7ff]/30' : 'bg-white/5 border-white/10'">
          <span class="material-symbols-outlined text-[24px] transition-colors"
                :class="connectedDevice ? 'text-[#ddb7ff]' : 'text-white/40'">smartphone</span>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="font-title-sm text-[20px] font-semibold truncate transition-colors"
                :class="connectedDevice ? 'text-[#e2e2e2]' : 'text-white/70'">
            {{ connectedDevice ? connectedDevice.name : (favoriteDevice ? 'Connetti a ' + favoriteDevice.name : 'Nessun dispositivo') }}
          </span>
          <span class="font-body-md text-sm transition-colors"
                :class="connectedDevice ? 'text-[#ddb7ff]' : 'text-red-400/70'">
            {{ connectedDevice ? 'Connected' : 'Disconnesso' }}
          </span>
        </div>
        <div class="ml-auto shrink-0" v-if="connectedDevice">
          <img :src="battery100" class="h-6 opacity-60" alt="Battery" />
        </div>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useBluetooth } from '@/composables/useBluetooth'
import { useAudioStore } from '@/stores/audio'
import songPlaceholder from '@/assets/song-placeholder.png'
import battery100 from '@/assets/battery/battery.100percent.svg'

const router = useRouter()
const { connectedDevice, favoriteDevice, connectToFavorite } = useBluetooth()

const audioStore = useAudioStore()
const { localCurrentSong, isLocalPlaying, localProgress } = storeToRefs(audioStore)

const formatDuration = (seconds: number) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const currentTitle = computed(() => {
  if (audioStore.currentSource === 'bluetooth' && audioStore.currentTrack) {
    return audioStore.currentTrack.title
  }
  return localCurrentSong.value?.title || 'Seleziona un brano'
})

const currentArtist = computed(() => {
  if (audioStore.currentSource === 'bluetooth' && audioStore.currentTrack) {
    return audioStore.currentTrack.artist
  }
  return localCurrentSong.value?.artist || 'Libreria'
})

const currentCover = computed(() => {
  if (audioStore.currentSource === 'bluetooth') {
    return songPlaceholder
  }
  return localCurrentSong.value?.coverUrl || songPlaceholder
})

const isPlaying = computed(() => {
  if (audioStore.currentSource === 'bluetooth') {
    return audioStore.playbackStatus === 'playing'
  }
  return isLocalPlaying.value
})

const progressPercent = computed({
  get() {
    if (audioStore.currentSource === 'bluetooth' && audioStore.currentTrack) {
      const duration = audioStore.currentTrack.duration || 1
      const pos = audioStore.currentTrack.position || 0
      return Math.min(100, Math.max(0, (pos / duration) * 100))
    }
    return localProgress.value
  },
  set(val: number) {
    if (audioStore.currentSource !== 'bluetooth') {
      audioStore.seekLocal(val)
    }
  }
})

const currentTimeText = computed(() => {
  if (audioStore.currentSource === 'bluetooth' && audioStore.currentTrack) {
    return formatDuration(audioStore.currentTrack.position || 0)
  }
  if (!localCurrentSong.value || !localCurrentSong.value.rawDuration) return '0:00'
  const currentSecs = (localProgress.value / 100) * localCurrentSong.value.rawDuration
  return formatDuration(currentSecs)
})

const remainingTimeText = computed(() => {
  if (audioStore.currentSource === 'bluetooth' && audioStore.currentTrack) {
    const duration = audioStore.currentTrack.duration || 0
    const pos = audioStore.currentTrack.position || 0
    return '-' + formatDuration(Math.max(0, duration - pos))
  }
  if (!localCurrentSong.value || !localCurrentSong.value.rawDuration) return '0:00'
  const currentSecs = (localProgress.value / 100) * localCurrentSong.value.rawDuration
  return '-' + formatDuration(localCurrentSong.value.rawDuration - currentSecs)
})

const togglePlay = () => {
  if (audioStore.currentSource === 'bluetooth') {
    if (isPlaying.value) {
      audioStore.pauseBluetooth()
    } else {
      audioStore.playBluetooth()
    }
  } else {
    audioStore.toggleLocalPlay()
  }
}

const handlePrev = () => {
  if (audioStore.currentSource === 'bluetooth') {
    audioStore.prevBluetooth()
  } else {
    audioStore.playPrevious()
  }
}

const handleNext = () => {
  if (audioStore.currentSource === 'bluetooth') {
    audioStore.nextBluetooth()
  } else {
    audioStore.playNext()
  }
}

const handleSeek = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (audioStore.currentSource !== 'bluetooth') {
    audioStore.seekLocal(Number(target.value))
  }
}
</script>