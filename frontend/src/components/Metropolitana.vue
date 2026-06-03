<script setup>
import { ref } from 'vue'
import axios from 'axios'

// --- Estados ---
const cargando = ref(false)
const errorMsg = ref(null)
const modoOrigen = ref('red')
const archivoSeleccionado = ref(null)

const dataPreview = ref(null)
const dataResultado = ref(null)

// --- Manejadores ---
const handleFileChange = (event) => {
  archivoSeleccionado.value = event.target.files[0]
}

// 1. PREVISUALIZACIÓN
const consultarPreview = async () => {
  cargando.value = true
  errorMsg.value = null
  dataResultado.value = null

  try {
    const formData = new FormData()
    if (modoOrigen.value === 'manual' && archivoSeleccionado.value) {
      formData.append('archivo', archivoSeleccionado.value)
    }
    
    // Apuntamos al nuevo endpoint de metropolitana
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/metropolitana/preview', formData)
    //console.log("Respuesta del servidor:", response.data);
    if (response.data.success) {
        dataPreview.value = response.data

    } else {
      errorMsg.value = response.data.error
    }
  } catch (err) {
    errorMsg.value = 'Error al generar la previsualización.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}

// 2. EJECUCIÓN FINAL
const ejecutarCarga = async () => {
  cargando.value = true
  errorMsg.value = null
  
  try {
    const formData = new FormData()
    if (modoOrigen.value === 'manual' && archivoSeleccionado.value) {
      formData.append('archivo', archivoSeleccionado.value)
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/metropolitana/ejecutar', formData)
    
    if (response.data.success) {
      dataResultado.value = response.data
      dataPreview.value = null
    } else {
      errorMsg.value = response.data.error || 'Error en la ejecución'
    }
  } catch (err) {
    errorMsg.value = 'Error crítico al ejecutar la carga.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}
</script>




<template>
  <div class="space-y-10">
    <div class="border-b border-slate-200 pb-4 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <span>🚇</span> Metropolitana
        </h1>
        <p class="text-sm text-slate-500 mt-1">Carga masiva de asignaciones diarias — Módulo de Gestión</p>
      </div>
      <div class="px-3 py-1 text-xs font-bold bg-emerald-100 text-emerald-700 rounded-full border border-emerald-200">
        ● Servidor API Activo
      </div>
    </div>

    <div v-if="cargando" class="bg-blue-50 border border-blue-200 text-blue-600 p-4 rounded-xl text-center text-sm font-medium animate-pulse">
      ⏳ Procesando datos en SQL Server... Por favor espere.
    </div>
    
    <div v-if="errorMsg" class="bg-rose-50 border border-rose-200 text-rose-600 p-4 rounded-xl text-sm">
      ⚠️ {{ errorMsg }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">1. Configuración del Origen</h2>
        
        <label class="flex items-start p-4 bg-slate-50 rounded-xl border cursor-pointer hover:border-indigo-500 transition" :class="{'border-indigo-500 bg-indigo-50/30': modoOrigen === 'red'}">
          <input type="radio" v-model="modoOrigen" value="red" class="mt-1 accent-indigo-600">
          <div class="ml-3">
            <span class="block text-sm font-semibold text-slate-800">Ruta automatizada (Red)</span>
            <span class="block text-xs text-slate-500 mt-1 font-mono break-all bg-white p-2 rounded border border-slate-200">
              \\192.168.1.249\...\Complementos_SQL_2026\..._subir.xlsx
            </span>
          </div>
        </label>

        <label class="flex items-start p-4 bg-slate-50 rounded-xl border cursor-pointer hover:border-indigo-500 transition" :class="{'border-indigo-500 bg-indigo-50/30': modoOrigen === 'manual'}">
          <input type="radio" v-model="modoOrigen" value="manual" class="mt-1 accent-indigo-600">
          <div class="ml-3 w-full">
            <span class="block text-sm font-semibold text-slate-800">Subir archivo Excel</span>
            <div v-if="modoOrigen === 'manual'" class="mt-3">
              <input type="file" @change="handleFileChange" accept=".xlsx" class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-200"/>
            </div>
          </div>
        </label>
      </div>

      <div class="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
        <div class="space-y-2">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">2. Acciones</h2>
         <p class="text-xs text-slate-500">Valida la estructura antes de procesar la carga.</p>
         </div>
        <div class="space-y-3 mt-4">
          <button @click="consultarPreview" :disabled="cargando" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-3 rounded-xl transition text-sm">🔍 Previsualizar</button>
          <button @click="ejecutarCarga" :disabled="cargando || !dataPreview" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition shadow-lg shadow-indigo-200 text-sm">🚀 Ejecutar Carga</button>
        </div>
      </div>
    </div>

    <div v-if="dataPreview || dataResultado" class="space-y-6">
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-white border rounded-2xl p-5 shadow-sm">
          <span class="text-[10px] font-bold text-slate-400 uppercase">Filas Excel</span>
          <span class="text-2xl font-black block">{{ dataPreview?.filas_excel ?? '--'}}</span>
        </div>
        <div class="bg-white border rounded-2xl p-5 shadow-sm">
          <span class="text-[10px] font-bold text-slate-400 uppercase">Registros en SQL</span>
          <span class="text-2xl font-black block">{{ dataPreview?.registros_antes ?? '--' }}</span>
        </div>
      </div>

      <div v-if="dataPreview" class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="text-slate-400 uppercase border-b">
            <tr class="bg-indigo-700 text-white"> 
              <th class="p-3 rounded-tl-xl">Nro</th>           
              <th class="p-3">Crédito_Doc</th>
              <th class="p-3">Crédito</th>
              <th class="p-3">Código</th>
              <th class="p-3">Cartera</th>
              <th class="p-3">Estado</th>
              <th class="p-3">Documento</th>
              <th class="p-3">Año</th>
              <th class="p-3 rounded-tr-xl whitespace-nowrap">Días Atraso</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="(fila, i) in dataPreview.preview" :key="i" class="hover:bg-slate-50">
              <td class="p-3 font-mono">{{ i + 1 }}</td>
              <td class="p-3 font-mono whitespace-nowrap">{{ fila['NroDocumento-Credito'] || '-' }}</td>
              <td class="p-3 whitespace-nowrap">{{ fila.Credito || '-' }}</td>
              <td class="p-3">{{ fila.Codigo || '-' }}</td>
              <td class="p-3">{{ fila.cartera_c || '-' }}</td>
              <td class="p-3 whitespace-nowrap">{{ fila.Estado || '-' }}</td>
              <td class="p-3">{{ fila.NroDocumento || '-' }}</td>
              <td class="p-3">{{ fila['año'] || '-' }}</td>
              <td class="p-3">{{ fila.DiasAtraso || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>