<template>
  <div class="flex-1 mt-4 mb-4 z-10 grid grid-cols-12 gap-[24px] h-full min-h-0">
    
    <!-- Left Panel: Media Player -->
    <div class="col-span-7 rounded-3xl overflow-hidden relative bg-white/5 backdrop-blur-2xl border border-white/10 group">
      <div class="absolute inset-0 bg-cover bg-center brightness-50 mix-blend-overlay group-hover:scale-105 transition-transform duration-1000 ease-out" :style="{ backgroundImage: `url(${songPlaceholder})` }"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-[#0e0e0e]/80 via-transparent to-[#0e0e0e]/30"></div>
      <div class="relative h-full flex flex-col justify-between p-[32px] z-10">
        <div>
          <h2 class="font-display-lg text-[48px] font-semibold leading-[1.1] tracking-[-0.02em] text-[#e2e2e2] mb-2">Midnight City</h2>
          <p class="font-title-sm text-[20px] font-semibold leading-[1.4] text-[#ddb7ff]">M83</p>
        </div>
        <div class="flex flex-col gap-6">
          <div class="w-full flex items-center gap-4">
            <span class="text-[#cfc2d6] text-sm font-medium">1:24</span>
            <div class="flex-1 h-1.5 bg-white/20 rounded-full overflow-hidden">
              <div class="h-full bg-[#ddb7ff] w-1/3 rounded-full shadow-[0_0_10px_rgba(221,183,255,0.5)]"></div>
            </div>
            <span class="text-[#cfc2d6] text-sm font-medium">-2:40</span>
          </div>
          <div class="flex justify-center items-center gap-8">
            <button class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
              <span class="material-symbols-outlined text-[28px] text-[#e2e2e2]">skip_previous</span>
            </button>
            <button @click="isPlaying = !isPlaying" class="w-[72px] h-[72px] flex items-center justify-center rounded-[24px] bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform shadow-[0_0_30px_rgba(221,183,255,0.3)]">
              <span class="material-symbols-outlined filled text-[40px]">{{ isPlaying ? 'pause' : 'play_arrow' }}</span>
            </button>
            <button class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10 backdrop-blur-md">
              <span class="material-symbols-outlined text-[28px] text-[#e2e2e2]">skip_next</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Area: OBD & BT -->
    <div class="col-span-5 flex flex-col gap-[24px] h-full">
      <!-- OBD Panel -->
      <div class="flex-1 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 flex flex-row justify-around items-center p-6 relative overflow-hidden">
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
      <div class="h-24 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 flex items-center px-6 gap-5">
        <div class="w-12 h-12 rounded-full bg-[#ddb7ff]/20 flex items-center justify-center border border-[#ddb7ff]/30">
          <span class="material-symbols-outlined text-[#ddb7ff] text-[24px]">smartphone</span>
        </div>
        <div class="flex flex-col">
          <span class="font-title-sm text-[20px] font-semibold text-[#e2e2e2]">iPhone di Marco</span>
          <span class="font-body-md text-sm text-[#ddb7ff]">Connected</span>
        </div>
        <div class="ml-auto">
          <img :src="battery100" class="h-6 opacity-60" alt="Battery" />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import songPlaceholder from '@/assets/song-placeholder.png'
import battery100 from '@/assets/battery/battery.100percent.svg'

const isPlaying = ref(false)
</script>