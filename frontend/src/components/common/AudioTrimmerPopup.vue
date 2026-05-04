<template>
  <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm px-8">
    <div class="w-full max-w-2xl bg-[#1c1c1e] border border-white/10 rounded-3xl p-8 shadow-2xl flex flex-col gap-8">
      
      <div>
        <h2 class="text-3xl font-semibold text-white mb-2">Taglia Audio</h2>
        <p class="text-white/60">Seleziona i nuovi limiti per il brano: {{ song?.title }}</p>
      </div>

      <div class="flex flex-col gap-6">
        <div class="flex justify-between text-sm font-medium text-white/50">
          <span>Inizio: {{ formatDuration(startTime) }}</span>
          <span>Fine: {{ formatDuration(endTime) }}</span>
        </div>
        
        <div class="relative w-full h-12 bg-white/5 rounded-2xl flex items-center px-4 overflow-hidden border border-white/10">
          <!-- Timeline progress background -->
          <div class="absolute top-0 bottom-0 bg-[#ddb7ff]/20 pointer-events-none" :style="{ left: `${(startTime / maxDuration) * 100}%`, right: `${100 - (endTime / maxDuration) * 100}%` }"></div>
          
          <input type="range" min="0" :max="maxDuration" v-model.number="startTime" class="w-full absolute inset-0 opacity-0 z-20 cursor-ew-resize" />
          <input type="range" min="0" :max="maxDuration" v-model.number="endTime" class="w-full absolute inset-0 opacity-0 z-30 cursor-ew-resize pointer-events-none" />
          
          <!-- Custom thumbs (visual only) -->
          <div class="absolute top-0 bottom-0 w-1 bg-[#ddb7ff] z-10 shadow-[0_0_10px_rgba(221,183,255,1)] pointer-events-none" :style="{ left: `calc(${(startTime / maxDuration) * 100}% - 2px)` }"></div>
          <div class="absolute top-0 bottom-0 w-1 bg-[#ddb7ff] z-10 shadow-[0_0_10px_rgba(221,183,255,1)] pointer-events-none" :style="{ left: `calc(${(endTime / maxDuration) * 100}% - 2px)` }"></div>
        </div>
        
        <div class="flex justify-between gap-4">
          <button @click="startTime = Math.max(0, startTime - 1)" class="p-2 rounded-lg bg-white/5 hover:bg-white/10">-1s Inizio</button>
          <button @click="startTime = Math.min(endTime - 1, startTime + 1)" class="p-2 rounded-lg bg-white/5 hover:bg-white/10">+1s Inizio</button>
          <div class="flex-1"></div>
          <button @click="endTime = Math.max(startTime + 1, endTime - 1)" class="p-2 rounded-lg bg-white/5 hover:bg-white/10">-1s Fine</button>
          <button @click="endTime = Math.min(maxDuration, endTime + 1)" class="p-2 rounded-lg bg-white/5 hover:bg-white/10">+1s Fine</button>
        </div>
      </div>

      <div class="flex justify-end gap-4 mt-4">
        <button @click="close" class="px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-white font-medium">Annulla</button>
        <button @click="confirm" class="px-6 py-3 rounded-xl bg-[#ddb7ff] text-[#490080] hover:scale-105 transition-transform font-bold">Salva Taglio</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

const props = defineProps<{
  isOpen: boolean
  song: any
}>()

const emit = defineEmits(['close', 'confirm'])

const startTime = ref(0)
const endTime = ref(100)
const maxDuration = computed(() => props.song?.rawDuration || 100)

watch(() => props.isOpen, (newVal) => {
  if (newVal && props.song) {
    startTime.value = 0
    endTime.value = props.song.rawDuration || 100
  }
})

const formatDuration = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const close = () => {
  emit('close')
}

const confirm = () => {
  if (startTime.value >= endTime.value) {
    alert("L'inizio deve essere prima della fine!")
    return
  }
  emit('confirm', { startTime: startTime.value, endTime: endTime.value })
}
</script>
