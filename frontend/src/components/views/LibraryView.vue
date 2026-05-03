<template>
  <div class="w-full h-full flex flex-col p-6">
    <!-- Header con tasto indietro -->
    <div class="flex items-center gap-4 mb-8">
      <button @click="$router.back()" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 transition-colors">
        <span class="material-symbols-outlined text-white">chevron_left</span>
      </button>
      <h1 class="text-3xl font-semibold text-white">La tua Libreria</h1>
    </div>
    
    <!-- Contenuto Libreria (Placeholder per ora) -->
    <div class="flex-1 flex items-center justify-center border-2 border-dashed border-white/10 rounded-2xl">
      <p class="text-white/40">Lista canzoni scaricate...</p>
    </div>
  </div>
</template>
