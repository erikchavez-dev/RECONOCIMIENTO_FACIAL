<template>
  <AdminLayout titulo="Asistencia">

    <!-- FILTROS -->
    <div class="filtros-card">
      <h3>Asistencia por Trabajador</h3>
      <div class="filtros">
        <div class="campo campo-trabajador" style="position:relative;">
          <label>Trabajador</label>
          <input v-model="buscar" @input="buscarTrabajadores" @blur="cerrarDropdown" type="text"
            placeholder="Ingrese DNI, nombre o apellido" class="input-buscar" />
          <div v-if="resultados.length" class="dropdown">
            <div v-for="t in resultados" :key="t.id" class="dropdown-item"
              @mousedown.prevent="seleccionarTrabajador(t)">
              {{ t.apellido_paterno }} {{ t.apellido_materno }}, {{ t.nombres }}
              <span class="dropdown-dni">{{ t.dni }}</span>
            </div>
          </div>
        </div>
        <div class="campo">
          <label>Desde</label>
          <input v-model="fechaInicio" type="date" />
        </div>
        <div class="campo">
          <label>Hasta</label>
          <input v-model="fechaFin" type="date" />
        </div>
        <button @click="cargar" :disabled="cargando || !trabajadorId" class="btn-buscar">
          {{ cargando ? 'Cargando...' : 'Ver asistencia' }}
        </button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <!-- INFO DEL TRABAJADOR -->
    <div v-if="datos" class="info-trabajador">
      <div class="info-nombre">
        {{ datos.trabajador.nombre }}
        <span class="info-dni"><b>DNI:</b> {{ datos.trabajador.dni }}</span>
        <span class="infor-cargo"><b>Cargo:</b> {{ datos.trabajador.cargo }}</span>
      </div>
    </div>

    <!-- RESUMEN -->
    <div v-if="datos" class="resumen-grid">
      <div class="resumen-card verde">
        <span class="res-valor">{{ datos.resumen.asistencias }}</span>
        <span class="res-label">Asistencias</span>
      </div>
      <div class="resumen-card amarillo">
        <span class="res-valor">{{ datos.resumen.tardanzas }}</span>
        <span class="res-label">Tardanzas</span>
      </div>
      <div class="resumen-card rojo">
        <span class="res-valor">{{ datos.resumen.faltas }}</span>
        <span class="res-label">Faltas</span>
      </div>
      <div class="resumen-card azul">
        <span class="res-valor">{{ datos.resumen.total_dias }}</span>
        <span class="res-label">Días Totales</span>
      </div>
    </div>

    <!-- TABLA -->
    <div v-if="datos" class="tabla-card">
      <div v-if="datos.dias.length === 0" class="vacio">
        No hay registros en este período
      </div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Entrada</th>
            <th>Salida</th>
            <th>Tiempo trabajado</th>
            <th>Resultado</th>
            <th>Editar</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dia in itemsPagina" :key="dia.fecha">
            <!-- FECHA -->
            <td class="celda-fecha">
              <span class="dia-semana">{{ dia.dia_semana }}</span>
              <span class="dia-fecha">{{ formatearFechaCorta(dia.fecha) }}</span>
            </td>

            <!-- ENTRADA -->
            <td>
              <div v-if="dia.entrada_hora" class="celda-marcacion">
                <span :class="['chip', dia.entrada_estado === 'PUNTUAL' ? 'chip-p' : 'chip-t']">
                  {{ dia.entrada_estado === 'PUNTUAL' ? 'P' : 'T' }}
                </span>
                <span class="hora-texto">{{ dia.entrada_hora }}</span>
              </div>
              <span v-else class="sin-dato">—</span>
            </td>

            <!-- SALIDA -->
            <td>
              <div v-if="dia.salida_hora" class="celda-marcacion">
                <span class="chip chip-s">S</span>
                <span class="hora-texto">{{ dia.salida_hora }}</span>
              </div>
              <span v-else class="sin-dato">—</span>
            </td>

            <!-- TIEMPO TRABAJADO -->
            <td>
              <span v-if="dia.tiempo_trabajado" class="tiempo-trabajado">
                {{ dia.tiempo_trabajado }}
              </span>
              <span v-else class="sin-dato">—</span>
            </td>

            <!-- RESULTADO -->
            <td>
              <span :class="['resultado-chip', claseResultado(dia.resultado)]">
                {{ dia.resultado }}
              </span>
            </td>
            <!-- EDITAR -->
            <td>
              <button class="btn-editar" @click="abrirModal(dia)">Editar</button>
            </td>
          </tr>

        </tbody>
      </table>
    </div>

    <!-- Paginador -->
    <PaginadorUI
      v-if="datos"
      :pagina-actual="paginaActual"
      :total-paginas="totalPaginas"
      :paginas-visibles="paginasVisibles"
      @ir="irA"
    />

    <div v-if="cargando" class="cargando">Cargando...</div>

    <Teleport to="body">
      <div v-if="modalAbierto" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal">
          <h4>Editar marcación</h4>
          <p class="modal-fecha">{{ modalDia?.dia_semana }} {{ formatearFechaCorta(modalDia?.fecha) }}</p>

          <div class="modal-campo">
            <label>Hora de entrada</label>
            <div class="hora-row">
              <input v-model="modalEntradaH" type="number" min="1" max="12" placeholder="HH" class="input-hora" />
              <span class="hora-sep">:</span>
              <input v-model="modalEntradaM" type="number" min="0" max="59" placeholder="MM" class="input-min" />
              <select v-model="modalEntradaPeriodo" class="sel-periodo">
                <option>AM</option>
                <option>PM</option>
              </select>
            </div>
          </div>

          <div class="modal-campo">
            <label>Hora de salida</label>
            <div class="hora-row">
              <input v-model="modalSalidaH" type="number" min="1" max="12" placeholder="HH" class="input-hora" />
              <span class="hora-sep">:</span>
              <input v-model="modalSalidaM" type="number" min="0" max="59" placeholder="MM" class="input-min" />
              <select v-model="modalSalidaPeriodo" class="sel-periodo">
                <option>AM</option>
                <option>PM</option>
              </select>
            </div>
          </div>

          <div class="modal-campo">
            <label>Motivo / justificación</label>
            <input v-model="modalMotivo" type="text" placeholder="Ej: El trabajador olvidó marcar..." />
          </div>

          <div v-if="modalError" class="error">{{ modalError }}</div>

          <div class="modal-footer">
            <button class="btn-cancelar" @click="cerrarModal">Cancelar</button>
            <button class="btn-guardar" :disabled="guardando" @click="guardarCambios">
              {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout   from '@/components/AdminLayout.vue'
import PaginadorUI   from '@/components/ui/PaginadorUI.vue'
import { usePaginacion } from '@/composables/usePaginacion'
import api from '@/services/api'

const trabajadoresOriginal = ref([])
const buscar     = ref('')
const resultados = ref([])
const trabajadorId  = ref(null)
const datos         = ref(null)
const cargando      = ref(false)
const error         = ref('')

// Días ordenados: más reciente primero (el backend los devuelve descendente
// pero por seguridad lo forzamos aquí también)
const diasOrdenados = computed(() =>
  datos.value
    ? [...datos.value.dias].sort((a, b) => b.fecha.localeCompare(a.fecha))
    : []
)

// Paginación cliente: 20 días por página sobre diasOrdenados
const { paginaActual, totalPaginas, paginasVisibles, itemsPagina, resetear, irA } =
  usePaginacion(diasOrdenados, 7)

const hoy      = new Date()
const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)


function formatearFechaLocal(date) {
  return date.toLocaleDateString('en-CA')
}

// Inicializar vacíos
const fechaInicio = ref('')
const fechaFin    = ref('')

async function cargar() {
  if (!trabajadorId.value) return
  error.value = ''
  cargando.value = true
  resetear()
  try {
    // Solo enviar fechas si el usuario las eligió
    const params = { trabajador_id: trabajadorId.value }
    if (fechaInicio.value && fechaFin.value) {
      params.fecha_inicio = fechaInicio.value
      params.fecha_fin    = fechaFin.value
    }

    const response = await api.get('/api/marcaciones/asistencia/admin/', { params })
    datos.value = response.data

    // Rellenar inputs con el período devuelto por el backend
    if (datos.value?.periodo) {
      fechaInicio.value = datos.value.periodo.inicio
      fechaFin.value    = datos.value.periodo.fin
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al cargar la asistencia'
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  try {
    let todos = [], pagina = 1
    while (true) {
      const res = await api.get(`/api/trabajadores/?page=${pagina}`)
      const lista = res.data.results || res.data.trabajadores || res.data
      if (!Array.isArray(lista)) break
      todos = [...todos, ...lista]
      if (!res.data.next && !res.data.total_paginas) break
      pagina++
    }
    trabajadoresOriginal.value = todos.sort((a, b) =>
      a.apellido_paterno.localeCompare(b.apellido_paterno)
    )
  } catch (e) {
    console.error('Error cargando trabajadores:', e)
  }
})

// AGREGA estas funciones nuevas:
function buscarTrabajadores() {
  trabajadorId.value = null
  const texto = buscar.value.toLowerCase().trim()
  if (!texto) { resultados.value = []; return }
  resultados.value = trabajadoresOriginal.value.filter(t =>
    t.dni.includes(texto) ||
    t.nombres.toLowerCase().includes(texto) ||
    t.apellido_paterno.toLowerCase().includes(texto) ||
    t.apellido_materno.toLowerCase().includes(texto)
  ).slice(0, 8)
}

function seleccionarTrabajador(t) {
  trabajadorId.value = t.id
  buscar.value = `${t.apellido_paterno} ${t.apellido_materno}, ${t.nombres}`
  resultados.value = []
}

function cerrarDropdown() {
  setTimeout(() => { resultados.value = [] }, 150)
}

// Modal
// Variables del modal
const modalAbierto       = ref(false)
const modalDia           = ref(null)
const modalEntradaH      = ref('')
const modalEntradaM      = ref('')
const modalEntradaPeriodo = ref('AM')
const modalSalidaH       = ref('')
const modalSalidaM       = ref('')
const modalSalidaPeriodo  = ref('PM')
const modalMotivo        = ref('')
const modalError         = ref('')
const guardando          = ref(false)

// Convierte "08:30:00 AM" o "08:30 AM" → { h: '08', m: '30', periodo: 'AM' }
function parsearHora12h(horaStr) {
  if (!horaStr) return { h: '', m: '', periodo: 'AM' }

  // Si viene en formato 24h (sin AM/PM), convertir
  if (!horaStr.includes('AM') && !horaStr.includes('PM')) {
    const [hStr, mStr] = horaStr.split(':')
    let h = parseInt(hStr)
    const m = mStr
    const periodo = h >= 12 ? 'PM' : 'AM'
    if (h > 12) h -= 12
    if (h === 0) h = 12
    return { h: String(h), m, periodo }
  }

  // Formato "08:30:45 AM"
  const [tiempo, periodo] = horaStr.trim().split(' ')
  const partes = tiempo.split(':')
  return { h: partes[0], m: partes[1], periodo }
}

// Convierte h, m, periodo → "HH:MM" en 24h para enviar al backend
function a24h(h, m, periodo) {
  let hNum = parseInt(h)
  const mStr = String(parseInt(m)).padStart(2, '0')
  if (periodo === 'AM' && hNum === 12) hNum = 0
  if (periodo === 'PM' && hNum !== 12) hNum += 12
  return `${String(hNum).padStart(2, '0')}:${mStr}`
}

function abrirModal(dia) {
  modalDia.value  = dia
  modalError.value = ''
  modalMotivo.value = ''

  const entrada = parsearHora12h(dia.entrada_hora)
  modalEntradaH.value       = entrada.h
  modalEntradaM.value       = entrada.m
  modalEntradaPeriodo.value = entrada.periodo

  const salida = parsearHora12h(dia.salida_hora)
  modalSalidaH.value       = salida.h
  modalSalidaM.value       = salida.m
  modalSalidaPeriodo.value = salida.periodo

  modalAbierto.value = true
}

function cerrarModal() {
  modalAbierto.value = false
}

async function guardarCambios() {
  if (!modalEntradaH.value || modalEntradaM.value === '') {
    modalError.value = 'La hora de entrada es obligatoria'
    return
  }
  guardando.value  = true
  modalError.value = ''

  const entradaStr = a24h(modalEntradaH.value, modalEntradaM.value, modalEntradaPeriodo.value)

  let salidaStr = null
  if (modalSalidaH.value !== '' && modalSalidaM.value !== '') {
    salidaStr = a24h(modalSalidaH.value, modalSalidaM.value, modalSalidaPeriodo.value)
  }

  try {
    await api.patch('/api/marcaciones/editar-admin/', {
      trabajador_id: trabajadorId.value,
      fecha:         modalDia.value.fecha,
      entrada_hora:  entradaStr,
      salida_hora:   salidaStr,
      motivo:        modalMotivo.value,
    })
    cerrarModal()
    await cargar()
  } catch (e) {
    modalError.value = e.response?.data?.error || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}


function formatearFechaCorta(fechaStr) {
  const [y, m, d] = fechaStr.split('-')
  return `${d}/${m}/${y}`
}

function claseResultado(resultado) {
  if (resultado === 'ASISTIÓ')   return 'res-asistio'
  if (resultado === 'TARDANZA')  return 'res-tardanza'
  if (resultado === 'SIN SALIDA') return 'res-sin-salida'
  return 'res-falta'
}
</script>

<style scoped src="./style.css"></style>