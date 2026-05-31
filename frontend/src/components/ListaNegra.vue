<script setup>
import { ref } from 'vue'
import axios from 'axios'

// --- Estados ---
const cargando = ref(false)
const errorMsg = ref(null)
const modoOrigen = ref('red')
const archivoSeleccionado = ref(null)
const mostrarModal = ref(false)

const dataPreview = ref(null)
const dataResultado = ref(null)

// --- Manejadores ---
const handleFileChange = (event) => {
  archivoSeleccionado.value = event.target.files[0]
}

const abrirConfirmacion = () => {
  mostrarModal.value = true
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
    
    // axios detectará automáticamente el Content-Type correcto para el FormData
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/lista-negra/preview', formData)

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

// 2. PROCESADOR DE ACCIÓN (Ejecución final)
// Hemos simplificado esto para que no haya ambigüedad en el envío
const procesarConAccion = async (accion) => {
  mostrarModal.value = false
  cargando.value = true
  errorMsg.value = null
  
  try {
    const formData = new FormData()
    
    if (modoOrigen.value === 'manual' && archivoSeleccionado.value) {
      formData.append('archivo', archivoSeleccionado.value)
    }
    
    // Inyectamos la acción exactamente como el backend la espera
    formData.append('accion', accion) 

    // POST directo sin forzar headers manualmente
    const response = await axios.post('http://127.0.0.1:8000/api/automatizaciones/lista-negra/ejecutar', formData)
    
    if (response.data.success) {
      dataResultado.value = response.data
      dataPreview.value = null
    } else {
      errorMsg.value = response.data.error || 'Error en la ejecución'
    }
  } catch (err) {
    errorMsg.value = 'Error crítico al ejecutar la carga.'
    console.log("Error detallado del servidor:", err.response.data);
    console.error(err)
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="space-y-10">
    <!-- Header -->
    <div class="border-b border-slate-200 pb-4 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <span>⚡</span> Lista Negra
        </h1>
        <p class="text-sm text-slate-500 mt-1">Carga masiva a SQL Server — Módulo de Gestión</p>
      </div>
      <div class="px-3 py-1 text-xs font-bold bg-emerald-100 text-emerald-700 rounded-full border border-emerald-200">
        ● Servidor API Activo
      </div>
    </div>

    <!-- Alertas -->
    <div v-if="cargando" class="bg-blue-50 border border-blue-200 text-blue-600 p-4 rounded-xl text-center text-sm font-medium animate-pulse">
      ⏳ Procesando requerimiento con la base de datos... Por favor espere.
    </div>
    
    <div v-if="errorMsg" class="bg-rose-50 border border-rose-200 text-rose-600 p-4 rounded-xl text-sm">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Configuración y Acciones -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">1. Configuración del Origen</h2>
        
        <label class="flex items-start p-4 bg-slate-50 rounded-xl border cursor-pointer hover:border-indigo-500 transition group" :class="{'border-indigo-500 bg-indigo-50/30': modoOrigen === 'red', 'border-slate-200': modoOrigen !== 'red'}">
          <input type="radio" v-model="modoOrigen" value="red" class="mt-1 accent-indigo-600">
          <div class="ml-3">
            <span class="block text-sm font-semibold text-slate-800">Ruta automatizada (Red)</span>
            <span class="block text-xs text-slate-500 mt-1 font-mono break-all bg-white p-2 rounded border border-slate-200">
              \\192.168.1.249\...\Complementos_SQL_2026\..._subir.xlsx
            </span>
          </div>
        </label>

        <label class="flex items-start p-4 bg-slate-50 rounded-xl border cursor-pointer hover:border-indigo-500 transition group" :class="{'border-indigo-500 bg-indigo-50/30': modoOrigen === 'manual', 'border-slate-200': modoOrigen !== 'manual'}">
          <input type="radio" v-model="modoOrigen" value="manual" class="mt-1 accent-indigo-600">
          <div class="ml-3 w-full">
            <span class="block text-sm font-semibold text-slate-800">Subir archivo Excel</span>
            <div v-if="modoOrigen === 'manual'" class="mt-3">
              <input type="file" @change="handleFileChange" accept=".xlsx" class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-200 hover:file:bg-slate-300"/>
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
          <button @click="abrirConfirmacion" :disabled="cargando || (!dataPreview && !dataResultado)" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition shadow-lg shadow-indigo-200 text-sm">🚀 Ejecutar Carga</button>
        </div>
      </div>
    </div>

    <!-- KPIs del Reporte -->
    <div v-if="dataPreview || dataResultado" class="space-y-4">
      <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">📊 Reporte de Operación</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Filas en Excel</span>
          <span class="text-2xl font-black text-slate-900 mt-1 block font-mono">{{ dataPreview?.filas_excel ?? '---' }}</span>
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <span class="text-[10px] font-bold text-amber-500 uppercase tracking-wider block">Duplicados Omitidos</span>
          <span class="text-2xl font-black text-amber-600 mt-1 block font-mono">{{ dataPreview?.duplicados_excel ?? '---' }}</span>
        </div>
        <div class="bg-white border rounded-2xl p-5 shadow-sm" :class="dataResultado ? 'border-emerald-500' : 'border-slate-200'">
          <span class="text-[10px] font-bold uppercase tracking-wider block" :class="dataResultado ? 'text-emerald-600' : 'text-slate-400'">Insertados en SQL</span>
          <span class="text-2xl font-black mt-1 block font-mono" :class="dataResultado ? 'text-emerald-700' : 'text-slate-400'">{{ dataResultado?.resumen?.filas_insertadas ? `+ ${dataResultado.resumen.filas_insertadas}` : '---' }}</span>
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Tiempo de Proceso</span>
          <span class="text-2xl font-black text-indigo-600 mt-1 block font-mono">{{ dataResultado?.resumen?.tiempo_total_segundos ? `${dataResultado.resumen.tiempo_total_segundos}s` : '---' }}</span>
        </div>
      </div>
    </div>

    <!-- Muestra de Datos -->
    <div v-if="dataPreview" class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-hidden">
      <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">👁️ Muestra de Registros</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="text-slate-400 uppercase">
            <tr class="border-b border-slate-100">
              <th class="p-3">Documento</th><th class="p-3">Teléfono</th><th class="p-3">Obs</th><th class="p-3">Cartera</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="(fila, i) in dataPreview.preview_filas" :key="i" class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-900">{{ fila.nro_documento }}</td>
              <td class="p-3 text-indigo-600 font-mono">{{ fila.telefono }}</td>
              <td class="p-3 text-slate-600">{{ fila.observaciones }}</td>
              <td class="p-3">{{ fila.cartera_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl border border-slate-100">
        <h3 class="font-bold text-lg mb-2">¿Cómo deseas proceder?</h3>
        <p class="text-slate-500 text-sm mb-6">Selecciona el modo de inserción.</p>
        <div class="flex flex-col gap-3">
          <button @click="procesarConAccion('limpiar')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold py-3 rounded-xl text-sm">Limpiar y Reemplazar</button>
          <button @click="procesarConAccion('insertar')" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl text-sm">Solo Insertar</button>
          <button @click="mostrarModal = false" class="bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold py-3 rounded-xl text-sm">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>
