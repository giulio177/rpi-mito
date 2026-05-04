<template>
  <div class="w-full h-full flex flex-col pt-6 px-8 pb-4 relative text-white min-h-0">
    <AudioTrimmerPopup :isOpen="isTrimmerOpen" :song="songToTrim" @close="isTrimmerOpen = false" @confirm="handleTrimConfirm" />
    
    <!-- Overlay Invisibile per chiusura (Click Outside) -->
    <div v-if="activeMenuId !== null" @click.stop="activeMenuId = null" class="fixed inset-0 z-40 bg-transparent"></div>

    <!-- Header -->
    <div class="flex items-center">
      <button @click="$router.back()" class="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center shrink-0 z-10">
        <span class="material-symbols-outlined text-[28px]">chevron_left</span>
      </button>
      <h1 class="text-3xl font-semibold ml-6 z-10">La tua Libreria</h1>
    </div>

    <!-- Lista Scrollabile -->
    <div class="flex-1 mt-8 overflow-y-auto pr-4 space-y-2 custom-scrollbar pb-36"
         :class="activeMenuId !== null ? 'relative z-50' : 'z-10'">
      <div 
        v-for="(song, index) in songs" 
        :key="song.id"
        @click="playSong(song)"
        class="w-full flex items-center p-4 rounded-2xl transition-colors border border-transparent group text-left relative cursor-pointer"
        :class="activeMenuId === song.id ? 'shadow-2xl bg-white/10' : (localCurrentSong?.id === song.id && isLocalPlaying ? 'bg-white/20 border-white/20' : 'bg-white/5 hover:bg-white/10 hover:border-white/10')"
        :style="{ zIndex: activeMenuId === song.id ? 50 : 1 }"
      >
        <!-- Copertina -->
        <img :src="song.coverUrl" class="w-16 h-16 rounded-xl object-cover shadow-md shrink-0" />
        
        <!-- Info (Centro) -->
        <div class="flex-1 min-w-0 ml-4 flex flex-col justify-center">
          <p class="text-xl font-medium truncate text-white">{{ song.title }}</p>
          <p class="text-sm text-[#ddb7ff] truncate mt-0.5">{{ song.artist }}</p>
        </div>

        <!-- Destra (Durata e Opzioni) -->
        <div class="flex items-center shrink-0 relative">
          <span class="text-white/50 text-sm mr-4">{{ song.duration }}</span>
          <button 
            @click.stop="activeMenuId = activeMenuId === song.id ? null : song.id" 
            class="w-12 h-12 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors"
          >
            <span class="material-symbols-outlined text-[24px]">more_vert</span>
          </button>

          <!-- Popover Context Menu -->
          <div v-if="activeMenuId === song.id" 
               @click.stop
               :class="[
                 'absolute right-0 w-56 bg-[#1c1c1e]/40 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-2 flex flex-col gap-1 animate-in fade-in zoom-in-95 duration-200',
                 (index >= songs.length - 2 && index >= 2) ? 'bottom-14 origin-bottom-right' : 'top-14 origin-top-right'
               ]"
               style="z-index: 9999;"
               >
            
            <!-- Pulsante Taglia -->
            <button @click.stop="openTrimmer(song)" class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/10 text-white transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">content_cut</span>
              <span class="font-medium text-sm">Taglia Audio</span>
            </button>

            <!-- Pulsante Rinomina -->
            <button @click.stop="handleRename(song)" class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/10 text-white transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">edit</span>
              <span class="font-medium text-sm">Rinomina</span>
            </button>

            <div class="h-[1px] w-full bg-white/10 my-1"></div>

            <!-- Pulsante Elimina -->
            <button @click.stop="handleDelete(song)" class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-red-500/20 text-red-400 hover:text-red-300 transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">delete</span>
              <span class="font-medium text-sm">Elimina</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useKeyboard } from '@/composables/useKeyboard'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
import songPlaceholder from '@/assets/song-placeholder.png'
import AudioTrimmerPopup from '@/components/common/AudioTrimmerPopup.vue'

const { openKeyboard } = useKeyboard()
const audioStore = useAudioStore()
const router = useRouter()
const { playLocalSong } = audioStore
const { localCurrentSong, isLocalPlaying } = storeToRefs(audioStore)

const songs = ref<any[]>([])

const formatDuration = (seconds: number) => {
  if (!seconds) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const fetchSongs = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/media/songs')
    const data = await res.json()
    songs.value = data.map((s: any) => ({
      ...s,
      rawDuration: s.duration,
      duration: formatDuration(s.duration),
      coverUrl: s.coverUrl || songPlaceholder
    }))
  } catch (err) {
    console.error('Failed to fetch songs:', err)
  }
}

onMounted(() => {
  fetchSongs()
})

const activeMenuId = ref<number | string | null>(null)

const playSong = (song: any) => {
  if (activeMenuId.value) {
    activeMenuId.value = null
    return // if menu was open, clicking row just closes menu
  }
  playLocalSong(song, songs.value)
  router.push('/music')
}

const handleRename = async (song: any) => {
  activeMenuId.value = null
  const newTitle = await openKeyboard(song.title, 'Rinomina Canzone')
  if (newTitle !== null && newTitle.trim() !== '') {
    const name = newTitle.trim()
    try {
      await fetch(`http://localhost:8000/api/media/songs/${song.id}/rename`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_name: name })
      })
      await fetchSongs()
    } catch(e) {
      console.error(e)
    }
  }
}

const handleDelete = async (song: any) => {
  activeMenuId.value = null
  try {
    await fetch(`http://localhost:8000/api/media/songs/${song.id}`, { method: 'DELETE' })
    await fetchSongs()
  } catch(e) {
    console.error(e)
  }
}

const isTrimmerOpen = ref(false)
const songToTrim = ref<any>(null)

const openTrimmer = (song: any) => {
  activeMenuId.value = null
  songToTrim.value = song
  isTrimmerOpen.value = true
}

const handleTrimConfirm = async (data: {startTime: number, endTime: number}) => {
  isTrimmerOpen.value = false
  if (!songToTrim.value) return
  
  try {
    await fetch(`http://localhost:8000/api/media/songs/${songToTrim.value.id}/trim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_time: data.startTime, end_time: data.endTime })
    })
    await fetchSongs() // refresh the list
  } catch (e) {
    console.error('Error trimming song', e)
  }
}
</script>
