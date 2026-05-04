<template>
  <div class="w-full h-full flex flex-col pt-6 px-8 pb-4 relative text-white min-h-0">
    
    <!-- Overlay Invisibile per chiusura (Click Outside) -->
    <div v-if="activeMenuId !== null" @click="activeMenuId = null" class="fixed inset-0 z-40"></div>

    <!-- Header -->
    <div class="flex items-center">
      <button @click="$router.back()" class="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center shrink-0 z-10">
        <span class="material-symbols-outlined text-[28px]">chevron_left</span>
      </button>
      <h1 class="text-3xl font-semibold ml-6 z-10">La tua Libreria</h1>
    </div>

    <!-- Lista Scrollabile -->
    <div class="flex-1 mt-8 overflow-y-auto pr-4 space-y-2 custom-scrollbar z-10 pb-36">
      <button 
        v-for="(song, index) in songs" 
        :key="song.id"
        class="w-full flex items-center p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 group text-left"
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
                 'absolute right-0 z-50 w-56 bg-[#1c1c1e]/40 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-2 flex flex-col gap-1 animate-in fade-in zoom-in-95 duration-200',
                 index >= songs.length - 2 ? 'bottom-14 origin-bottom-right' : 'top-14 origin-top-right'
               ]">
            
            <!-- Pulsante Taglia -->
            <button class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/10 text-white transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">content_cut</span>
              <span class="font-medium text-sm">Taglia Audio</span>
            </button>

            <!-- Pulsante Rinomina -->
            <button class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/10 text-white transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">edit</span>
              <span class="font-medium text-sm">Rinomina</span>
            </button>

            <div class="h-[1px] w-full bg-white/10 my-1"></div>

            <!-- Pulsante Elimina -->
            <button class="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-red-500/20 text-red-400 hover:text-red-300 transition-colors text-left">
              <span class="material-symbols-outlined text-[20px]">delete</span>
              <span class="font-medium text-sm">Elimina</span>
            </button>
          </div>
        </div>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import songPlaceholder from '@/assets/song-placeholder.png'

const songs = ref([
  { id: 1, title: 'Midnight City', artist: 'M83', duration: '4:04', coverUrl: songPlaceholder },
  { id: 2, title: 'Blinding Lights', artist: 'The Weeknd', duration: '3:20', coverUrl: songPlaceholder },
  { id: 3, title: 'Starboy', artist: 'The Weeknd', duration: '3:50', coverUrl: songPlaceholder },
  { id: 4, title: 'Nightcall', artist: 'Kavinsky', duration: '4:19', coverUrl: songPlaceholder },
  { id: 5, title: 'Get Lucky', artist: 'Daft Punk', duration: '6:09', coverUrl: songPlaceholder },
])

const activeMenuId = ref<number | string | null>(null)
</script>
