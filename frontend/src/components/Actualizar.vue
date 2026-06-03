<script setup>
import { ref } from 'vue'
import axios from 'axios'

// --- Estados ---
const cargando = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)
const archivoSeleccionado = ref(null)

const mes = ref(6) 
const anio = ref(2026) 
const opcionProceso = ref('4') 

const dataPreview = ref(null)
const dataResultado = ref(null)

// --- Manejadores ---
const handleFileChange = (event) => {
  archivoSeleccionado.value = event.target.files[0]
}

// 1. PREVISUALIZACIÓN
const consultarPreview = async () => {
  if (!archivoSeleccionado.value) return errorMsg.value = "Selecciona un archivo primero."
  
  cargando.value = true
  errorMsg.value = null
  dataResultado.value = null
  
  try {
    const formData = new FormData()
    formData.append('archivo', archivoSeleccionado.value)
    
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/actualizar-preview', formData)
    
    if (response.data.success) {
      dataPreview.value = response.data
    } else {
      errorMsg.value = response.data.error
    }
  } catch (err) {
    errorMsg.value = 'Error al previsualizar.'
  } finally {
    cargando.value = false
  }
}

// 2. EJECUCIÓN
const ejecutarCarga = async () => {
  cargando.value = true
  errorMsg.value = null
  
  try {
    const formData = new FormData()
    formData.append('archivo', archivoSeleccionado.value)
    formData.append('opcion', opcionProceso.value)
    formData.append('mes', mes.value)
    formData.append('anio', anio.value)
    
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/actualizar-ejecutar', formData)
    
    if (response.data.success) {
      dataResultado.value = response.data
      successMsg.value = response.data.proceso
      dataPreview.value = null 
    } else {
      errorMsg.value = response.data.error
    }
  } catch (err) {
    errorMsg.value = 'Error en la ejecución.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-8 space-y-8">
    
    <div class="space-y-1">
      <h1 class="text-2xl font-bold text-slate-800">Carga y Actualización de Cartera</h1>
      <p class="text-sm text-slate-400 font-medium">Configura los parámetros antes de procesar la base de datos</p>
    </div>

    <div v-if="successMsg" class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl text-sm font-semibold flex items-center shadow-sm">
      <span class="mr-2">✨</span> {{ successMsg }}
    </div>


    <div class="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm shadow-slate-100">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-3">
          <label class="text-xs font-bold uppercase text-slate-400 tracking-wider">Archivo Excel</label>
          <div class="relative border-2 border-dashed border-slate-200 rounded-2xl p-4 hover:border-indigo-300 transition-colors">
            <input type="file" @change="handleFileChange" class="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 cursor-pointer"/>
          </div>
        </div>

        <div class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-400">Mes</label>
              <input type="number" v-model="mes" class="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium text-slate-700">
            </div>
            <div class="space-y-2">
              <label class="text-xs font-bold text-slate-400">Año</label>
              <input type="number" v-model="anio" class="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium text-slate-700">
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-bold text-slate-400">Acción a ejecutar</label>
            <select v-model="opcionProceso" class="w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium text-slate-700 cursor-pointer">
              <option value="4">Solo subir datos</option>
              <option value="1">Actualizar Administrada</option>
              <option value="2">Actualizar Hipotecario</option>
              <option value="3">Actualizar Convenio</option>
            </select>
          </div>
        </div>
      </div>

      <div class="flex gap-4 mt-8 pt-8 border-t border-slate-100">
        <button @click="consultarPreview" :disabled="cargando" class="px-6 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-300 text-slate-700 font-bold text-sm transition">🔍 Previsualizar data</button>
        <button @click="ejecutarCarga" :disabled="cargando || !archivoSeleccionado" class="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm transition shadow-indigo-200">🚀 Ejecutar Procesos</button>
      </div>
    </div>

    
    <div v-if="dataPreview || dataResultado" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Filas Excel</span>
        <span class="text-xl font-black text-slate-600">{{ dataPreview?.total_filas ?? '0' }}</span>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Estado Proceso</span>
        <span class="text-sm font-bold text-indigo-600 mt-1 truncate">{{ dataResultado?.proceso ?? 'Pendiente' }}</span>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Base Destino</span>
        <span class="text-sm font-bold text-slate-700 mt-1">Asignacion (SQL)</span>
      </div>
    </div>


    <div v-if="dataPreview" class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left">
          <thead class="text-slate-400 uppercase tracking-wider">
            <tr class="bg-indigo-700 text-white">
              <th v-for="col in dataPreview.columnas" :key="col" class="p-1 border-b border-slate-100 text-[11px] text-white whitespace-nowrap">{{ col }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="(fila, index) in dataPreview.preview" :key="index" class="hover:bg-slate-50/50">
              <td v-for="(val, key) in fila" :key="key" class="p-1 text-slate-600 text-[11px] whitespace-nowrap">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>