<template>
  <div class="w-full h-full relative flex px-8 pt-8 pb-28 gap-10 text-white min-h-0">
    
    <!-- Action Bar Fissa (Memoria Muscolare) -->
    <div class="absolute top-2 right-2 z-50 flex gap-4">
      <button @click="showLyrics = !showLyrics" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shadow-lg">
        <span class="material-symbols-outlined text-[24px]" :class="showLyrics ? 'text-[#ddb7ff]' : 'text-white/70'">lyrics</span>
      </button>
      <button class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shadow-lg">
        <span class="material-symbols-outlined text-[24px] text-[#ddb7ff]">download</span>
      </button>
      <button @click="$router.push('/library')" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shadow-lg">
        <span class="material-symbols-outlined text-[24px] text-white/70">queue_music</span>
      </button>
    </div>

    <!-- STATO A: Player Standard -->
    <template v-if="!showLyrics">
      <!-- Sinistra: Copertina Album -->
      <div class="w-[40%] max-w-[320px] aspect-square bg-[#1c1c1e] rounded-[32px] overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/5 shrink-0 z-10 relative my-auto">
        <img :src="currentCover" class="w-full h-full object-cover" />
      </div>

      <!-- Destra: Info e Controlli -->
      <div class="flex-1 flex flex-col justify-between h-full pt-8 pb-4 min-w-0 z-10 relative">
        
        <!-- Titolo e Artista -->
        <div class="pr-5
        0">
          <h1 class="font-display-lg text-[56px] font-semibold leading-tight tracking-tight text-white mb-2 line-clamp-1">{{ currentTitle }}</h1>
          <p class="font-title-sm text-[28px] font-medium text-[#ddb7ff]">{{ currentArtist }}</p>
        </div>

        <!-- Playback Controls -->
        <div class="flex flex-col gap-6">
          <!-- Progress Bar -->
          <div class="w-full flex items-center gap-4">
            <span class="text-white/50 text-sm font-medium w-12 text-right">{{ currentTimeText }}</span>
            <div class="relative flex-1 h-2 bg-white/20 rounded-full">
              <!-- Parte Riempita -->
              <div class="absolute top-0 left-0 h-full bg-[#ddb7ff] rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)] pointer-events-none" :style="{ width: progressPercent + '%' }"></div>
              <!-- Input Range Invisibile Interattivo -->
              <input type="range" min="0" max="100" v-model.number="progressPercent" @input="handleSeek" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer m-0 z-10" />
            </div>
            <span class="text-white/50 text-sm font-medium w-12 text-left">{{ remainingTimeText }}</span>
          </div>

          <!-- Main Buttons -->
          <div class="flex justify-between items-center px-4">
            <button @click="audioStore.toggleShuffle()" class="transition-colors" :class="shuffleEnabled ? 'text-[#ddb7ff] drop-shadow-[0_0_8px_rgba(221,183,255,0.8)]' : 'text-white/40 hover:text-white/70'">
              <span class="material-symbols-outlined text-[28px]">shuffle</span>
            </button>
            
            <div class="flex items-center gap-6">
              <button @click="handlePrev" class="w-14 h-14 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
                <span class="material-symbols-outlined text-[32px] text-white">skip_previous</span>
              </button>
              <button @click="togglePlay" class="w-[72px] h-[72px] flex items-center justify-center rounded-[24px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)]">
                <span class="material-symbols-outlined filled text-[48px]">{{ isPlaying ? 'pause' : 'play_arrow' }}</span>
              </button>
              <button @click="handleNext" class="w-14 h-14 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
                <span class="material-symbols-outlined text-[32px] text-white">skip_next</span>
              </button>
            </div>

            <button @click="audioStore.toggleRepeat()" class="transition-colors" :class="repeatEnabled ? 'text-[#ddb7ff] drop-shadow-[0_0_8px_rgba(221,183,255,0.8)]' : 'text-white/40 hover:text-white/70'">
              <span class="material-symbols-outlined text-[28px]">repeat</span>
            </button>
          </div>
        </div>

      </div>
    </template>

    <!-- STATO B: Modalità Lyrics -->
    <template v-else>
      <!-- Sinistra: Lyrics Area -->
      <div class="w-[60%] flex flex-col gap-6 h-full justify-center pr-2 mask-image-linear-y relative overflow-hidden z-10">
        <p class="text-2xl font-medium text-white/40 truncate">Waiting in a car</p>
        <p class="text-2xl font-medium text-white/40 truncate">Waiting for a ride in the dark</p>
        <p class="text-4xl font-bold text-white py-2 transform scale-105 origin-left transition-transform">The city is my church</p>
        <p class="text-2xl font-medium text-white/40 truncate">It wraps me in its blinding twilight</p>
        <p class="text-2xl font-medium text-white/40 truncate">Waiting in a car</p>
      </div>

      <!-- Divisore Verticale -->
      <div class="w-[1px] h-[80%] my-auto bg-white/10 mx-6 shrink-0 z-10 relative"></div>

      <!-- Destra: Mini Player -->
      <div class="flex-1 flex flex-col items-center justify-center h-full pt-12 gap-6 relative z-10">
        
        <!-- Info (Cover, Title, Artist) -->
        <div class="flex flex-col items-center gap-4">
          <div class="w-32 h-32 bg-[#1c1c1e] rounded-2xl overflow-hidden shadow-2xl border border-white/5 shrink-0">
            <img :src="currentCover" class="w-full h-full object-cover" />
          </div>
          <div class="text-center">
            <h2 class="font-display-lg text-[22px] font-semibold text-white mb-0.5 line-clamp-1">{{ currentTitle }}</h2>
            <p class="font-title-sm text-[15px] font-medium text-[#ddb7ff]">{{ currentArtist }}</p>
          </div>
        </div>

        <!-- Playback Controls -->
        <div class="flex flex-col gap-4 w-full">
          <!-- Progress Bar -->
          <div class="w-full flex items-center gap-3">
            <span class="text-white/50 text-xs font-medium w-10 text-right">{{ currentTimeText }}</span>
            <div class="relative flex-1 h-1.5 bg-white/20 rounded-full">
              <!-- Parte Riempita -->
              <div class="absolute top-0 left-0 h-full bg-[#ddb7ff] rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)] pointer-events-none" :style="{ width: progressPercent + '%' }"></div>
              <!-- Input Range Invisibile Interattivo -->
              <input type="range" min="0" max="100" v-model.number="progressPercent" @input="handleSeek" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer m-0 z-10" />
            </div>
            <span class="text-white/50 text-xs font-medium w-10 text-left">{{ remainingTimeText }}</span>
          </div>

          <!-- Main Buttons (No Shuffle/Repeat) -->
          <div class="flex items-center justify-center gap-6 mt-2">
            <button @click="handlePrev" class="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shrink-0">
              <span class="material-symbols-outlined text-[12px] text-white">skip_previous</span>
            </button>
            <button @click="togglePlay" class="w-12 h-12 flex items-center justify-center rounded-[18px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)] shrink-0">
              <span class="material-symbols-outlined filled text-[18px]">{{ isPlaying ? 'pause' : 'play_arrow' }}</span>
            </button>
            <button @click="handleNext" class="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shrink-0">
              <span class="material-symbols-outlined text-[12px] text-white">skip_next</span>
            </button>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAudioStore } from '@/stores/audio'
import songPlaceholder from '@/assets/song-placeholder.png'

const audioStore = useAudioStore()
const { localCurrentSong, isLocalPlaying, localProgress, shuffleEnabled, repeatEnabled } = storeToRefs(audioStore)

const showLyrics = ref(false)

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