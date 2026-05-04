<template>
  <div class="fixed inset-x-0 bottom-0 z-[200] bg-[#1c1c1e]/90 backdrop-blur-3xl border-t border-white/10 rounded-t-[40px] p-6 shadow-[0_-20px_50px_rgba(0,0,0,0.5)] flex flex-col gap-4 animate-in slide-in-from-bottom-full duration-300">
    
    <!-- Area di Testo -->
    <div class="flex flex-col items-center mb-2">
      <span class="text-sm font-medium text-[#ddb7ff] mb-2 uppercase tracking-widest">{{ keyboardTitle }}</span>
      <div class="flex items-center h-12">
        <span class="text-3xl font-medium text-white">{{ inputValue }}</span>
        <span class="w-0.5 h-8 bg-[#ddb7ff] animate-pulse ml-1"></span>
      </div>
    </div>

    <!-- Layout Tastiera -->
    <div class="flex flex-col gap-3">
      <!-- Riga 1 -->
      <!-- Riga 1 -->
      <div class="flex gap-2">
        <button v-for="char in activeRow1" :key="char" @click="appendChar(char)" class="h-14 flex-1 bg-white/10 hover:bg-white/20 active:scale-95 rounded-2xl flex items-center justify-center text-2xl font-medium transition-all text-white border border-white/5">
          {{ char }}
        </button>
      </div>

      <!-- Riga 2 -->
      <div class="flex gap-2 px-6">
        <button v-for="char in activeRow2" :key="char" @click="appendChar(char)" class="h-14 flex-1 bg-white/10 hover:bg-white/20 active:scale-95 rounded-2xl flex items-center justify-center text-2xl font-medium transition-all text-white border border-white/5">
          {{ char }}
        </button>
      </div>

      <!-- Riga 3 -->
      <div class="flex gap-2">
        <button @click="isShift = !isShift" :disabled="isSymbols" class="h-14 flex-[1.5] bg-white/5 hover:bg-white/10 active:scale-95 rounded-2xl flex items-center justify-center text-2xl transition-all text-white border border-white/5 disabled:opacity-50">
          <span v-if="!isSymbols" class="material-symbols-outlined">{{ isShift ? 'keyboard_capslock' : 'shift' }}</span>
          <span v-else class="text-lg text-white/30 font-medium">#+=</span>
        </button>
        <button v-for="char in activeRow3" :key="char" @click="appendChar(char)" class="h-14 flex-1 bg-white/10 hover:bg-white/20 active:scale-95 rounded-2xl flex items-center justify-center text-2xl font-medium transition-all text-white border border-white/5">
          {{ char }}
        </button>
        <button @click="backspace" class="h-14 flex-[1.5] bg-white/5 hover:bg-white/10 active:scale-95 rounded-2xl flex items-center justify-center text-2xl transition-all text-white border border-white/5">
          <span class="material-symbols-outlined">backspace</span>
        </button>
      </div>

      <!-- Riga 4 (Controlli) -->
      <div class="flex gap-2 mt-2">
        <button @click="isSymbols = !isSymbols" class="h-14 flex-[1.5] bg-white/5 hover:bg-white/10 active:scale-95 rounded-2xl flex items-center justify-center text-xl font-medium transition-all text-white border border-white/5">
          {{ isSymbols ? 'ABC' : '123' }}
        </button>
        <button @click="close(false)" class="h-14 flex-[2] bg-red-500/10 hover:bg-red-500/20 active:scale-95 rounded-2xl flex items-center justify-center text-xl font-medium transition-all text-red-400 border border-red-500/20">
          Annulla
        </button>
        <button @click="appendChar(' ')" class="h-14 flex-[4] bg-white/10 hover:bg-white/20 active:scale-95 rounded-2xl flex items-center justify-center text-2xl transition-all border border-white/5">
          <span class="material-symbols-outlined text-white/50">space_bar</span>
        </button>
        <button @click="close(true)" class="h-14 flex-[2.5] bg-[#ddb7ff] hover:bg-[#c99cf5] active:scale-95 rounded-2xl flex items-center justify-center text-xl font-bold transition-all text-[#490080] shadow-[0_0_20px_rgba(221,183,255,0.3)]">
          Conferma
        </button>
      </div>
    </div>
    
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useKeyboard } from '@/composables/useKeyboard'

const { inputValue, keyboardTitle, appendChar, backspace, close } = useKeyboard()

const isShift = ref(true)
const isSymbols = ref(false)

const alphaRow1 = ['q','w','e','r','t','y','u','i','o','p']
const alphaRow2 = ['a','s','d','f','g','h','j','k','l']
const alphaRow3 = ['z','x','c','v','b','n','m']

const symRow1 = ['1','2','3','4','5','6','7','8','9','0']
const symRow2 = ['-','/',':',';','(',')','$','&','@','"']
const symRow3 = ['.',',','?','!','\'']

const activeRow1 = computed(() => {
  const row = isSymbols.value ? symRow1 : alphaRow1
  return isShift.value && !isSymbols.value ? row.map(c => c.toUpperCase()) : row
})

const activeRow2 = computed(() => {
  const row = isSymbols.value ? symRow2 : alphaRow2
  return isShift.value && !isSymbols.value ? row.map(c => c.toUpperCase()) : row
})

const activeRow3 = computed(() => {
  const row = isSymbols.value ? symRow3 : alphaRow3
  return isShift.value && !isSymbols.value ? row.map(c => c.toUpperCase()) : row
})
</script>
