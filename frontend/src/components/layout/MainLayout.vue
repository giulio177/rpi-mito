<template>
  <div class="fixed inset-0 bg-black flex items-center justify-center overflow-hidden">
    <!-- Schermo con scaling dinamico -->
    <div 
      class="relative bg-[#0e0e0e] rounded-[40px] overflow-hidden border border-white/5 shadow-2xl flex flex-col p-6 origin-center"
      :style="{ width: '1024px', height: '600px', transform: `scale(${scale})` }"
    >
      <!-- Global Ambient Background -->
      <div class="absolute inset-0 bg-cover bg-center opacity-30 blur-[60px] pointer-events-none z-0 scale-110" :style="{ backgroundImage: `url(${songPlaceholder})` }"></div>
      <div class="absolute inset-0 bg-gradient-to-b from-[#0e0e0e]/30 via-[#0e0e0e]/60 to-[#0e0e0e]/95 pointer-events-none z-0"></div>

      <!-- Ambient Glows -->
      <div class="absolute -top-20 -left-20 w-[400px] h-[400px] bg-[#ddb7ff] rounded-full blur-[120px] opacity-20 pointer-events-none z-0"></div>
      <div class="absolute -bottom-40 -right-20 w-[500px] h-[500px] bg-blue-600 rounded-full blur-[120px] opacity-20 pointer-events-none z-0"></div>
      
      <TopBar />
      <router-view class="flex-1 mt-4 mb-4 z-10" />
      <BottomNav />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import TopBar from '@/components/common/TopBar.vue'
import BottomNav from '@/components/common/BottomNav.vue'
import songPlaceholder from '@/assets/song-placeholder.png'

const scale = ref(1)

const updateScale = () => {
  const winW = window.innerWidth
  const winH = window.innerHeight
  // Calcola la scala per far stare sempre il 1024x600 nello schermo
  scale.value = Math.min(winW / 1024, winH / 600)
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScale)
})
</script>