<template>
  <AdminLayout titulo="Asistencia">

    <!-- FILTROS -->
    <div class="filtros-card">
      <h3>Asistencia por Trabajador</h3>
      <div class="filtros">
        <div class="campo campo-trabajador" style="position:relative;">
          <label>Trabajador</label>
          <input v-model="buscar" @input="buscarTrabajadores" @blur="cerrarDropdown" type="text"
            placeholder="Buscar por DNI, nombre o apellido..." class="input-buscar" />
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
        <span class="info-dni">DNI: {{ datos.trabajador.dni }}</span>
      </div>
      <div class="info-cargo">{{ datos.trabajador.cargo }}</div>
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
        <span class="res-label">Días registrados</span>
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
          <tr v-for="dia in datos.dias" :key="dia.fecha">
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
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const trabajadoresOriginal = ref([])
const buscar     = ref('')
const resultados = ref([])
const trabajadorId  = ref(null)
const datos         = ref(null)
const cargando      = ref(false)
const error         = ref('')

const hoy      = new Date()
const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)


function formatearFechaLocal(date) {
  return date.toLocaleDateString('en-CA')
}

const fechaInicio = ref(formatearFechaLocal(primerDia))
const fechaFin    = ref(formatearFechaLocal(hoy))

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

async function cargar() {
  if (!trabajadorId.value) return
  error.value = ''
  cargando.value = true
  try {
    const response = await api.get('/api/marcaciones/asistencia/admin/', {
      params: {
        trabajador_id: trabajadorId.value,
        fecha_inicio:  fechaInicio.value,
        fecha_fin:     fechaFin.value,
      }
    })
    datos.value = response.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al cargar la asistencia'
  } finally {
    cargando.value = false
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

<style scoped>
.filtros-card {
  background: white;
  border-radius: 10px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
  margin-bottom: 20px;
}

.filtros-card h3 {
  font-size: 1.45em;
  color: #1a3a6b;
  margin-bottom: 16px;
  font-weight: 700;
}


.filtros {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  flex-wrap: wrap;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.campo-trabajador {
  flex: 1;
  min-width: 220px;
}

.campo label {
  font-size: 1em;
  font-weight: 600;
  color: #1a3a6b;
}

.campo input,
.sel-trabajador {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
}

.campo input:focus,
.sel-trabajador:focus {
  outline: none;
  border-color: #1a3a6b;
}

.sel-trabajador {
  width: 100%;
}

.btn-buscar {
  padding: 8px 20px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.88rem;
  white-space: nowrap;
}

.btn-buscar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* INFO TRABAJADOR */
.info-trabajador {
  background: #eff6ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  border-left: 4px solid #3b82f6;
}
.info-nombre {
  font-weight: 700;
  color: #1a3a6b;
  font-size: 1.2em;
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-dni {
  font-size: 0.85em;
  color: #6b7280;
  font-weight: 400;
}

.info-cargo {
  font-size: 1em;
  color: #4b5563;
  margin-top: 2px;
}

/* RESUMEN */
.resumen-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
  margin-bottom: 20px;
}

@media (max-width: 600px) {
  .resumen-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.resumen-card {
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-left: 5px solid transparent;
}
.resumen-card:hover {
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-left: 5px solid transparent;
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      border-left 0.3s ease,
      box-shadow 0.3s ease;
}

.resumen-card.verde:hover {
  transform: scale(1.09);
  background: #90ee98;
}

.resumen-card.amarillo:hover {
  background: #faeb42;
  transform: scale(1.09);
}

.resumen-card.rojo:hover {
  background: #f15b5b;
  transform: scale(1.09);
}

.resumen-card.azul:hover {
  background: #3384ee;
  transform: scale(1.09);
}

.resumen-card.verde {
  background: #f0fdf4;
  border-left-color: #16a34a;
}

.resumen-card.amarillo {
  background: #fefce8;
  border-left-color: #ffa200;
}

.resumen-card.rojo {
  background: #fef2f2;
  border-left-color: #ff0000;
}

.resumen-card.azul {
  background: #eff6ff;
  border-left-color: #166bf3;
}

.res-valor {
  font-size: 1.8rem;
  font-weight: 800;
  color: #111827;
}

.res-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

/* TABLA */
.tabla-card {
  background: white; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07); overflow: auto;
}
.tabla { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.tabla th {
  background: #1a3a6b; color: white;
  padding: 12px 16px; text-align: left; font-weight: 600;
}
.tabla td { padding: 12px 16px; border-bottom: 1px solid #f0f4f8; color: #333; }
.tabla tr:hover { background: #f8fafc; }

.celda-fecha { display: flex; flex-direction: column; gap: 2px; }
.dia-semana { font-weight: 700; color: #1a3a6b; font-size: 0.82rem; }
.dia-fecha  { font-size: 0.82rem; color: #6b7280; }

.celda-marcacion { display: flex; align-items: center; gap: 8px; }
.chip {
  width: 24px; height: 24px; border-radius: 6px;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.75rem; flex-shrink: 0;
}
.chip-p { background: #dcfce7; color: #16a34a; }
.chip-t { background: #fef9c3; color: #b45309; }
.chip-s { background: #dbeafe; color: #1d4ed8; }
.hora-texto { font-size: 0.82rem; color: #374151; font-weight: 500; }
.tiempo-trabajado { font-family: monospace; font-size: 0.88rem; color: #1a3a6b; font-weight: 600; }
.resultado-chip { padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.res-asistio    { background: #dcfce7; color: #16a34a; }
.res-tardanza   { background: #fef9c3; color: #b45309; }
.res-sin-salida { background: #dbeafe; color: #1d4ed8; }
.res-falta      { background: #fee2e2; color: #dc2626; }
.sin-dato { color: #d1d5db; font-size: 0.85rem; }
.vacio    { text-align: center; padding: 40px; color: #9ca3af; }
.cargando { text-align: center; padding: 40px; color: #9ca3af; }
.error { background: #fef2f2; color: #dc2626; padding: 10px; border-radius: 6px; font-size: 0.85rem; margin-top: 12px; }


/* para el ultimo cambio qeu hice */
.input-buscar {
  padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px;
  font-size: 0.88rem; width: 100%;
}
.input-buscar:focus { outline: none; border-color: #1a3a6b; }
.dropdown {
  position: absolute; top: 100%; left: 0; right: 0;
  background: white; border: 1px solid #ddd; border-radius: 6px;
  max-height: 200px; overflow-y: auto; z-index: 50;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.dropdown-item {
  padding: 8px 12px; cursor: pointer; font-size: 0.85rem;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #f0f4f8;
}
.dropdown-item:hover { background: #f8fafc; }
.dropdown-dni { font-size: 0.75rem; color: #9ca3af; }
.btn-editar {
  padding: 4px 12px; border: 1px solid #ddd; border-radius: 6px;
  background: white; cursor: pointer; font-size: 0.78rem; color: #4b5563;
}
.btn-editar:hover { background: #f8fafc; border-color: #1a3a6b; color: #1a3a6b; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal {
  background: white; border-radius: 12px; padding: 24px;
  width: 400px; max-width: 95vw; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.modal h4 { font-size: 1rem; color: #1a3a6b; font-weight: 700; margin-bottom: 4px; }
.modal-fecha { font-size: 0.82rem; color: #6b7280; margin-bottom: 18px; }
.modal-campo { margin-bottom: 14px; display: flex; flex-direction: column; gap: 4px; }
.modal-campo label { font-size: 0.78rem; font-weight: 600; color: #1a3a6b; }
.modal-campo input {
  padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.88rem;
}
.modal-campo input:focus { outline: none; border-color: #1a3a6b; }
.opcional { font-weight: 400; color: #9ca3af; }
.modal-footer { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
.btn-cancelar {
  padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px;
  background: white; cursor: pointer; font-size: 0.88rem; color: #4b5563;
}
.btn-guardar {
  padding: 8px 20px; background: #1a3a6b; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 0.88rem;
}
.btn-guardar:disabled { opacity: 0.5; cursor: not-allowed; }


.hora-row {
  display: flex; align-items: center; gap: 6px;
}
.input-hora {
  width: 52px; padding: 8px 6px; border: 1px solid #ddd;
  border-radius: 6px; font-size: 0.88rem; text-align: center;
}
.input-min {
  width: 52px; padding: 8px 6px; border: 1px solid #ddd;
  border-radius: 6px; font-size: 0.88rem; text-align: center;
}
.hora-sep { font-weight: 700; color: #1a3a6b; }
.sel-periodo {
  padding: 8px 8px; border: 1px solid #ddd; border-radius: 6px;
  font-size: 0.88rem; color: #374151; cursor: pointer;
}


/* para el responsive */


</style>