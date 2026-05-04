<template>
  <div class="flex-none h-10 z-10 flex justify-between items-center px-4">
    <div class="text-[#cfc2d6] font-medium tracking-wide">
      10:42 PM | 22°C
    </div>
    <div class="flex items-center gap-4 text-[#cfc2d6]">
      <span class="material-symbols-outlined text-[20px]">wifi</span>
      <span class="material-symbols-outlined text-[20px]">bluetooth</span>
      <img :src="battery100" class="h-5 opacity-80" alt="Battery" />
    </div>
  </div>
</template>

<script setup lang="ts">
import battery100 from '@/assets/battery/battery.100percent.svg'
// In futuro qui collegheremo i WebSocket per l'ora e i sensori
</script>