<script setup>
import { ref } from 'vue'
import axios from 'axios'

// Estados para controlar la interfaz
const cargando = ref(false)
const errorMsg = ref(null)
const modoOrigen = ref('red') // 'red' o 'manual'
const archivoSeleccionado = ref(null)

// Estados para almacenar la respuesta de la API
const dataPreview = ref(null)
const dataResultado = ref(null)

// Capturar el archivo si deciden subirlo manualmente
const handleFileChange = (event) => {
  archivoSeleccionado.value = event.target.files[0]
}

// 1. LLAMADA AL ENDPOINT DE PREVISUALIZACIÓN
const consultarPreview = async () => {
  cargando.value = true
  errorMsg.value = null
  dataResultado.value = null
  
  try {
    const formData = new FormData()
    if (modoOrigen.value === 'manual' && archivoSeleccionado.value) {
      formData.append('file', archivoSeleccionado.value)
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/lista-negra/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    dataPreview.value = response.data
  } catch (err) {
    errorMsg.value = 'Error al generar la previsualización. Verifica el archivo o la red.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}

// 2. LLAMADA AL ENDPOINT DE EJECUCIÓN (INSERCIÓNA SQL SERVER)
const ejecutarCarga = async () => {
  cargando.value = true
  errorMsg.value = null
  
  try {
    const formData = new FormData()
    if (modoOrigen.value === 'manual' && archivoSeleccionado.value) {
      formData.append('file', archivoSeleccionado.value)
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/lista-negra/ejecutar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    dataResultado.value = response.data
    dataPreview.value = null 
  } catch (err) {
    errorMsg.value = 'Error crítico al insertar en SQL Server.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
    <div class="max-w-7xl mx-auto space-y-10">
      
      <div class="border-b border-slate-800 pb-4 flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <span>⚡</span> Panel de Automatizaciones
          </h1>
          <p class="text-sm text-slate-400 mt-1">Carga masiva a SQL Server — Módulo Lista Negra</p>
        </div>
        <div class="px-3 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">
          ● Servidor API Activo
        </div>
      </div>

      <div v-if="cargando" class="bg-blue-500/10 border border-blue-500/20 text-blue-400 p-4 rounded-xl text-center text-sm font-medium animate-pulse">
        ⏳ Procesando requerimiento con la base de datos... Por favor espere.
      </div>
      
      <div v-if="errorMsg" class="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl text-sm">
        ⚠️ {{ errorMsg }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="md:col-span-2 bg-slate-800/50 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">1. Configuración del Origen</h2>
          
          <label class="flex items-start p-4 bg-slate-800 rounded-lg border cursor-pointer hover:border-blue-500 transition group" :class="{'border-blue-500 bg-slate-800/80': modoOrigen === 'red', 'border-slate-700': modoOrigen !== 'red'}">
            <input type="radio" v-model="modoOrigen" value="red" class="mt-1 text-blue-500 focus:ring-0">
            <div class="ml-3">
              <span class="block text--sm font-medium text-white group-hover:text-blue-400 transition">Ruta automatizada del mes actual (Red)</span>
              <span class="block text-xs text-slate-400 mt-1 font-mono break-all bg-slate-900/50 p-2 rounded">
                \\192.168.1.249\...\Complementos_SQL_2026\..._subir.xlsx
              </span>
            </div>
          </label>

          <label class="flex items-start p-4 bg-slate-800 rounded-lg border cursor-pointer hover:border-blue-500 transition group" :class="{'border-blue-500 bg-slate-800/80': modoOrigen === 'manual', 'border-slate-700': modoOrigen !== 'manual'}">
            <input type="radio" v-model="modoOrigen" value="manual" class="mt-1 text-blue-500 focus:ring-0">
            <div class="ml-3 w-full">
              <span class="block text-sm font-medium text-white group-hover:text-blue-400 transition">Subir archivo Excel manualmente</span>
              <div v-if="modoOrigen === 'manual'" class="mt-3">
                <input type="file" @change="handleFileChange" accept=".xlsx" class="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-slate-700 file:text-slate-200 hover:file:bg-slate-600"/>
              </div>
            </div>
          </label>
        </div>

        <div class="bg-slate-800/50 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div class="space-y-2">
            <h2 class="text-m font-semibold uppercase tracking-wider text-slate-400">2. Acciones</h2>
            <p class="text-xs text-slate-400">Genera primero la previsualización para validar la estructura antes de procesar la carga masiva.</p>
          </div>

          <div class="space-y-3 mt-4">
            <button @click="consultarPreview" :disabled="cargando" class="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-2.5 px-4 rounded-lg transition shadow-lg shadow-blue-600/20 text-sm">
              🔍 Consultar Previsualización
            </button>
            <button @click="ejecutarCarga" :disabled="cargando || (!dataPreview && !dataResultado)" class="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold py-2.5 px-4 rounded-lg transition shadow-lg shadow-emerald-600/20 text-sm tracking-wide">
              🚀 Confirmar y Ejecutar Carga
            </button>
          </div>
        </div>
      </div>

      <div v-if="dataPreview && dataPreview.duplicados_excel > 0" class="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
        <span class="text-amber-500 text-lg">⚠️</span>
        <div>
          <h4 class="text-sm font-semibold text-amber-400">Advertencia de duplicidad</h4>
          <p class="text-xs text-slate-300 mt-0.5">Se han detectado <span class="font-bold text-amber-300 font-mono">{{ dataPreview.duplicados_excel }}</span> registros duplicados dentro del archivo. El sistema los omitirá automáticamente.</p>
        </div>
      </div>

      <div v-if="dataPreview" class="bg-slate-800/50 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">👁️ Muestra de Registros (Primeras 10 filas)</h2>
        <div class="overflow-x-auto rounded-lg border border-slate-800">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-slate-900 text-slate-300 font-medium uppercase tracking-wider border-b border-slate-800">
                <th class="p-3">Nro Documento</th>
                <th class="p-3">Teléfono</th>
                <th class="p-3">Observaciones</th>
                <th class="p-3">Cartera ID</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300 font-mono">
              <tr v-for="(fila, index) in dataPreview.rows_muestra" :key="index" class="hover:bg-slate-800/30 transition">
                <td class="p-3 text-white font-medium">{{ fila.nro_documento }}</td>
                <td class="p-3 text-emerald-400">{{ fila.telefono }}</td>
                <td class="p-3 truncate max-w-xs">{{ fila.observacion || 'SIN OBSERVACIÓN' }}</td>
                <td class="p-3">{{ fila.id_cartera }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="dataPreview || dataResultado" class="space-y-4">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">📊 Reporte de Operación</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          
          <div class="bg-slate-800/30 border border-slate-800 rounded-xl p-4">
            <span class="text-xs text-slate-400 font-medium block">Filas en Excel</span>
            <span class="text-xl font-bold text-white mt-1 block font-mono">
              {{ dataPreview ? dataPreview.total_excel : dataResultado.total_procesados }}
            </span>
          </div>

          <div class="bg-slate-800/30 border border-slate-800 rounded-xl p-4">
            <span class="text-xs text-slate-400 font-medium block">Duplicados Omitidos</span>
            <span class="text-xl font-bold text-amber-400 mt-1 block font-mono">
              {{ dataPreview ? dataPreview.duplicados_excel : dataResultado.duplicados_omitidos }}
            </span>
          </div>

          <div class="bg-slate-800/30 border rounded-xl p-4" :class="dataResultado ? 'bg-emerald-500/5 border-emerald-500/20' : 'border-slate-800'">
            <span class="text-xs font-medium block" :class="dataResultado ? 'text-emerald-400' : 'text-slate-400'">Insertados en SQL</span>
            <span class="text-xl font-bold mt-1 block font-mono" :class="dataResultado ? 'text-emerald-400' : 'text-slate-300'">
              {{ dataResultado ? `+ ${dataResultado.insertados}` : '---' }}
            </span>
          </div>

          <div class="bg-slate-800/30 border border-slate-800 rounded-xl p-4">
            <span class="text-xs text-slate-400 font-medium block">Tiempo de Proceso</span>
            <span class="text-xl font-bold text-blue-400 mt-1 block font-mono">
              {{ dataResultado ? `${dataResultado.tiempo_segundos}s` : '---' }}
            </span>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>