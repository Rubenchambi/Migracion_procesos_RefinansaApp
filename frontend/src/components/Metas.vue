<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// --- Estados ---
const metas = ref([])
const carterasMaestra = ref([]) 
const opcionesConfig = ref({ tramos: [], subcarteras: [], tipos: [] })
const metaForm = ref({})
const showModal = ref(false)
const modo = ref('crear')
const cargando = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
// Estado para la notificación moderna
const esperandoConfirmacion = ref(false)
const notificacion = ref({ show: false, text: '', tipo: 'success' })

const mostrarNotificacion = (texto, tipo = 'success') => {
    notificacion.value = { show: true, text: texto, tipo }
    setTimeout(() => { notificacion.value.show = false }, 3000)
}

// --- Carga de Datos ---
const fetchData = async (page = 1) => {
    cargando.value = true
    try {
        const res = await axios.get(`http://127.0.0.1:8000/api/metas/listar-metas?page=${page}&page_size=5`)
        metas.value = res.data.items
        totalPages.value = res.data.pages
        currentPage.value = page
        const resMaestra = await axios.get('http://127.0.0.1:8000/api/metas/carteras-maestra')
        carterasMaestra.value = resMaestra.data
    } catch (err) {
        console.error("Error:", err)
    } finally {
        cargando.value = false
    }
}

onMounted(fetchData)

// --- KPIs Computados ---
const totalCarteras = computed(() => new Set(metas.value.map(m => m.cartera_id)).size)
const montoTotalMeta = computed(() => metas.value.reduce((acc, m) => acc + (parseFloat(m.meta_monto) || 0), 0))
const promedioCumplimiento = computed(() => metas.value.length > 0 ? (metas.value.length) : 0)

// --- Lógica de Formulario ---
const abrirModal = (m = null) => {
    if (m) {
        metaForm.value = { ...m }
        modo.value = 'editar'
        handleCarteraChange()
    } else {
        metaForm.value = { 
            cartera_id: '', cartera_nombre: '', tramo: '', tipo_meta: 'GENERAL',
            subcartera: '', asesor_nombre: '', meta_monto: 0, meta_porcentaje: 0,
            mes_asignacion: new Date().getMonth() + 1, año_asignacion: 2026 
        }
        modo.value = 'crear'
    }
    showModal.value = true
}

const handleCarteraChange = async () => {
    try {
        const res = await axios.get(`http://127.0.0.1:8000/api/metas/configuracion-cartera/${metaForm.value.cartera_id}`)
        metaForm.value.cartera_nombre = res.data.cartera_nombre
        opcionesConfig.value = {
            tramos: res.data.tramos,
            subcarteras: res.data.subcarteras,
            tipos: res.data.tipos
        }
    } catch (e) {
        console.error("Error al cargar configuración:", e)
    }
}

const ejecutarGuardado = async () => {
    // Si viene del botón "Confirmar" del popup, ejecutamos
    try {
        await axios.post('http://127.0.0.1:8000/api/metas/guardar-meta', metaForm.value)
        showModal.value = false
        esperandoConfirmacion.value = false // Cerramos el popup
        fetchData()
        mostrarNotificacion("¡Meta guardada con éxito!", "success")
    } catch (err) {
        esperandoConfirmacion.value = false
        mostrarNotificacion("Error al procesar la meta", "error")
    }
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-6 space-y-8 text-xs">
    
    <div v-if="notificacion.show" 
         class="fixed bottom-6 right-6 z-[100] px-6 py-3 rounded-2xl shadow-2xl text-white font-bold transition-all"
         :class="notificacion.tipo === 'success' ? 'bg-indigo-600' : 'bg-red-600'">
        {{ notificacion.text }}
    </div>

    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-black text-slate-800 tracking-tight">Panel de Metas</h1>
        <p class="text-slate-400 font-medium">Configuración de objetivos comerciales por cartera</p>
      </div>
      <button @click="abrirModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-2xl font-bold shadow-lg shadow-indigo-100 transition-all active:scale-95">
        Nueva Meta
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div v-for="(val, label, index) in { 'Carteras': totalCarteras, 'Monto Total Meta': 'S/ ' + montoTotalMeta.toLocaleString(), 'Registros': metas.length, 'Estado': 'Activo' }" :key="index" 
           class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-center">
        <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{{ label }}</span>
        <span class="text-2xl font-black text-slate-700">{{ val }}</span>
      </div>
    </div>

    <div class="bg-white rounded-[1rem] border border-slate-100 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/50 text-[10px] font-black text-slate-400 uppercase tracking-tighter">
              <th class="p-4 border-b">Cartera</th>
              <th class="p-4 border-b">Tramo / Sub</th>
              <th class="p-4 border-b">Tipo</th>
              <th class="p-4 border-b">Asesor</th>
              <th class="p-4 border-b">Monto Meta</th>
              <th class="p-4 border-b">Periodo</th>
              <th class="p-4 border-b text-center">Acciones</th>
            </tr>
          </thead>
          <tbody class="text-[11px] font-medium text-slate-600 divide-y divide-slate-50">
            <tr v-for="m in metas" :key="m.id" class="hover:bg-indigo-50/30 transition-colors">
              <td class="p-4 font-black text-indigo-600 cursor-pointer" @click="abrirModal(m)">{{ m.cartera_nombre }}</td>
              <td class="p-4">
                <div class="flex flex-col">
                    <span>{{ m.tramo || '-' }}</span>
                    <span class="text-[9px] text-slate-400">{{ m.subcartera || 'Sin subcartera' }}</span>
                </div>
              </td>
              <td class="p-4"><span class="px-2 py-1 bg-slate-100 rounded-md text-[9px] font-bold">{{ m.tipo_meta }}</span></td>
              <td class="p-4">{{ m.asesor_nombre || 'General' }}</td>
              <td class="p-4 font-black text-slate-800">S/ {{ m.meta_monto }}</td>
              <td class="p-4">{{ m.mes_asignacion }}/{{ m.año_asignacion }}</td>
              <td class="p-4 text-center">
                <button @click="abrirModal(m)" class="bg-slate-100 p-2 rounded-lg hover:bg-indigo-100 text-indigo-600 transition-colors">
                  ⚙️ Editar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-between items-center p-4 border-t">
            <button :disabled="currentPage === 1" @click="fetchData(currentPage - 1)" class="px-4 py-2 bg-slate-100 hover:bg-indigo-500 rounded-lg text-xs font-bold disabled:opacity-50">Anterior</button>
            <span class="text-xs font-bold text-slate-500">Página {{ currentPage }} de {{ totalPages }}</span>
            <button :disabled="currentPage >= totalPages" @click="fetchData(currentPage + 1)" class="px-4 py-2 bg-slate-100 hover:bg-indigo-500 rounded-lg text-xs font-bold disabled:opacity-50">Siguiente</button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div class="bg-white w-full max-w-2xl rounded-[2rem] shadow-2xl p-10 space-y-6">
        <div class="flex justify-between items-start">
            <h2 class="text-2xl font-black text-slate-800">{{ modo === 'crear' ? 'Nueva Configuración de Meta' : 'Actualizar Meta: ' + metaForm.cartera_nombre }}</h2>
            <button @click="showModal = false" class="text-slate-300 hover:text-slate-500 text-2xl">✕</button>
        </div>

        <div class="grid grid-cols-2 gap-5">
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Cartera (ID)</label>
            <select v-model="metaForm.cartera_id" @change="handleCarteraChange" class="w-full h-[52px] px-4 bg-white border border-slate-200 rounded-2xl text-sm font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer shadow-sm hover:border-slate-300">
                <option value="" disabled>Seleccione Cartera</option>
                <option v-for="c in carterasMaestra" :key="c.cartera_id" :value="c.cartera_id">{{ c.cartera_id }} - {{ c.cartera_nombre }}</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Nombre Cartera</label>
            <input v-model="metaForm.cartera_nombre" readonly class="w-full p-3.5 bg-slate-100 border-none rounded-2xl text-sm font-bold text-slate-500 outline-none">
          </div>
          
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Tramo</label>
            <select v-model="metaForm.tramo" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
                <option v-for="t in opcionesConfig.tramos" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Tipo de Meta</label>
            <select v-model="metaForm.tipo_meta" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
                <option v-for="tp in opcionesConfig.tipos" :value="tp">{{ tp }}</option>
            </select>
          </div>
          <div class="space-y-1 col-span-2">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Sub Cartera</label>
            <select v-model="metaForm.subcartera" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
                <option v-for="s in opcionesConfig.subcarteras" :value="s">{{ s }}</option>
            </select>
          </div>
          
          <div class="space-y-1 col-span-2">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Nombre Asesor</label>
            <input v-model="metaForm.asesor_nombre" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Monto Meta (S/)</label>
            <input v-model="metaForm.meta_monto" type="number" class="w-full p-3.5 bg-emerald-50 text-emerald-700 border-none rounded-2xl text-sm font-black outline-none">
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Meta Porcentaje (%)</label>
            <input v-model="metaForm.meta_porcentaje" type="number" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Mes</label>
            <input v-model="metaForm.mes_asignacion" type="number" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Año</label>
            <input v-model="metaForm.año_asignacion" type="number" class="w-full p-3.5 bg-slate-50 border-none rounded-2xl text-sm font-bold outline-none">
          </div>
        </div>

        <button @click="esperandoConfirmacion = true" 
                class="w-full max-w-sm mx-auto block py-4 bg-indigo-600 text-white rounded-2xl text-sm font-black shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all hover:scale-[1.02] active:scale-[0.98]">
            {{ modo === 'crear' ? '🚀 Registrar Meta' : '💾 Guardar Cambios' }}
        </button>

      </div>
    </div>
  </div>
    <div v-if="esperandoConfirmacion" class="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-[100] p-4">
        <div class="bg-white w-full max-w-sm rounded-[2rem] shadow-2xl p-8 space-y-6 text-center animate-in fade-in zoom-in duration-300">
            <div>
                <div class="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl shadow-inner">⚡</div>
                <h3 class="text-xl font-black text-slate-800">¿Estás seguro?</h3>
                <p class="text-sm text-slate-400 mt-2">Esta acción guardará los cambios de forma permanente en el sistema.</p>
            </div>
            
            <div class="flex gap-4">
                <button @click="esperandoConfirmacion = false" 
                        class="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-bold hover:bg-slate-200 transition-all">
                    Cancelar
                </button>
                <button @click="ejecutarGuardado" 
                        class="flex-1 py-4 bg-indigo-600 text-white rounded-2xl font-black shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:scale-[1.02] transition-all">
                    Confirmar
                </button>
            </div>
        </div>
    </div>

</template>