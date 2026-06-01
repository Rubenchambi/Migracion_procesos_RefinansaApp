<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        <h1 class="font-bold text-xl text-indigo-600 tracking-tight whitespace-nowrap">⚡ AutoPanel</h1>

        <div class="flex-1 mx-8 max-w-lg">
          <input type="text" placeholder="Buscar módulos..." 
                 class="w-full bg-slate-100 border-none rounded-lg py-2 px-4 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition">
        </div>

        <div class="flex items-center gap-4">
          <div class="text-right hidden md:block">
            <p class="text-xs font-bold text-slate-900">Hola, Admin</p>
          </div>
          <button class="text-xs font-bold text-indigo-600 hover:text-indigo-800 px-3 py-1 bg-indigo-50 rounded-lg">Salir</button>
          
          <button @click="esHorizontal = !esHorizontal" class="p-2 hover:bg-slate-100 rounded-lg transition-all">
            <svg class="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!esHorizontal" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto p-6 flex gap-6" :class="esHorizontal ? 'flex-col' : 'flex-row'">
      
    <aside :class="[
      esHorizontal 
        ? 'w-full flex-row gap-2 border-b border-slate-200 mb-6 pb-4' 
        : 'w-64 flex-col gap-3 bg-slate-100/50 p-6 rounded-2xl h-[calc(100vh-120px)] border border-slate-200/60 sticky top-24'
    ]" class="flex transition-all duration-500 ease-in-out">
      
      <button v-for="mod in modulos" :key="mod.id" 
        @click="actual = mod.id"
        :class="actual === mod.id ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900'"
        class="px-5 py-3 rounded-xl text-sm font-bold transition-all text-left">
        {{ mod.nombre }}
      </button>
      
      <div :class="esHorizontal ? 'hidden' : 'mt-auto pt-6 border-t border-slate-200/50'">
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest px-2">Sistema v2026</p>
      </div>
    </aside>

      <main class="flex-1">
        <component :is="componenteActivo" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ListaNegra from './components/ListaNegra.vue'
import Metropolitana from './components/Metropolitana.vue'

const esHorizontal = ref(false)
const actual = ref('lista-negra')

const modulos = [
  { id: 'lista-negra', nombre: 'Lista Negra', comp: ListaNegra },
  { id: 'metropolitana', nombre: 'Metropolitana DXD', comp: Metropolitana },
  { id: 'requerimientos', nombre: 'Requerimientos' },
  { id: 'predictivos', nombre: 'Predictivos Alfin' }
]

const componenteActivo = computed(() => {
  const mod = modulos.find(m => m.id === actual.value)
  return mod ? mod.comp : null
})
</script>