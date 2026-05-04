<template>
  <div class="w-full h-full relative flex px-8 pt-8 pb-2 gap-10 text-white min-h-0">
    
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
        <img :src="songPlaceholder" class="w-full h-full object-cover" />
      </div>

      <!-- Destra: Info e Controlli -->
      <div class="flex-1 flex flex-col justify-between h-full pt-4 pb-4 min-w-0 z-10 relative">
        
        <!-- Titolo e Artista -->
        <div class="pr-40">
          <h1 class="font-display-lg text-[56px] font-semibold leading-tight tracking-tight text-white mb-2 line-clamp-1">Midnight City</h1>
          <p class="font-title-sm text-[28px] font-medium text-[#ddb7ff]">M83</p>
        </div>

        <!-- Playback Controls -->
        <div class="flex flex-col gap-6">
          <!-- Progress Bar -->
          <div class="w-full flex items-center gap-4">
            <span class="text-white/50 text-sm font-medium">1:24</span>
            <div class="flex-1 h-2 bg-white/20 rounded-full overflow-hidden cursor-pointer">
              <div class="h-full bg-[#ddb7ff] w-1/3 rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)]"></div>
            </div>
            <span class="text-white/50 text-sm font-medium">-2:40</span>
          </div>

          <!-- Main Buttons -->
          <div class="flex justify-between items-center px-4">
            <button class="text-white/40 hover:text-[#ddb7ff] transition-colors">
              <span class="material-symbols-outlined text-[28px]">shuffle</span>
            </button>
            
            <div class="flex items-center gap-6">
              <button class="w-14 h-14 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
                <span class="material-symbols-outlined text-[32px] text-white">skip_previous</span>
              </button>
              <button class="w-[72px] h-[72px] flex items-center justify-center rounded-[24px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)]">
                <span class="material-symbols-outlined filled text-[48px]">pause</span>
              </button>
              <button class="w-14 h-14 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
                <span class="material-symbols-outlined text-[32px] text-white">skip_next</span>
              </button>
            </div>

            <button class="text-white/40 hover:text-[#ddb7ff] transition-colors">
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
            <img :src="songPlaceholder" class="w-full h-full object-cover" />
          </div>
          <div class="text-center">
            <h2 class="font-display-lg text-[22px] font-semibold text-white mb-0.5 line-clamp-1">Midnight City</h2>
            <p class="font-title-sm text-[15px] font-medium text-[#ddb7ff]">M83</p>
          </div>
        </div>

        <!-- Playback Controls -->
        <div class="flex flex-col gap-4 w-full">
          <!-- Progress Bar -->
          <div class="w-full flex items-center gap-3">
            <span class="text-white/50 text-xs font-medium">1:24</span>
            <div class="flex-1 h-1.5 bg-white/20 rounded-full overflow-hidden cursor-pointer">
              <div class="h-full bg-[#ddb7ff] w-1/3 rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)]"></div>
            </div>
            <span class="text-white/50 text-xs font-medium">-2:40</span>
          </div>

          <!-- Main Buttons (No Shuffle/Repeat) -->
          <div class="flex justify-center items-center gap-6">
            <button class="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shrink-0">
              <span class="material-symbols-outlined text-[12px] text-white">skip_previous</span>
            </button>
            <button class="w-12 h-12 flex items-center justify-center rounded-[18px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)] shrink-0">
              <span class="material-symbols-outlined filled text-[18px]">pause</span>
            </button>
            <button class="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md shrink-0">
              <span class="material-symbols-outlined text-[12px] text-white">skip_next</span>
            </button>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import songPlaceholder from '@/assets/song-placeholder.png'

const showLyrics = ref(false)
</script>