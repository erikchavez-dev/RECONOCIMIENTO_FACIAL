<!-- ReportesView.vue — Reportes de asistencia por rango de fechas -->
<template>
  <AdminLayout titulo="Reportes">

    <div class="filtros-card">
      <h3>Reportes de Asistencia</h3>

      <div class="filtros">
        <div class="campo">
          <label>Fecha inicio</label>
          <input v-model="fechaInicio" type="date" />
        </div>

        <div class="campo">
          <label>Fecha fin</label>
          <input v-model="fechaFin" type="date" />
        </div>

        <!-- Filtro por estado del trabajador -->
        <div class="campo">
          <label>Filtrar por</label>
          <select v-model="filtroEstado" @change="onFiltroEstadoCambio">
            <option value="todos">Todos los trabajadores</option>
            <option value="activos">Solo trabajadores activos</option>
            <option value="inactivos">Solo trabajadores inactivos</option>
          </select>
        </div>

        <!-- Trabajador específico (opcional) -->
        <div class="campo">
          <label>Trabajador (opcional)</label>
          <select v-model="trabajadorId">
            <option value="">
              {{
                filtroEstado === 'activos'   ? 'Todos los activos' :
                filtroEstado === 'inactivos' ? 'Todos los inactivos' :
                'Todos los trabajadores'
              }}
            </option>
            <option v-for="t in trabajadoresFiltrados" :key="t.id" :value="t.id">
              {{ t.nombres }} {{ t.apellido_paterno }} — {{ t.dni }}
              {{ !t.activo ? '(Inactivo)' : '' }}
            </option>
          </select>
        </div>
      </div>

      <div class="botones-filtro">
        <button @click="verReporte" :disabled="cargando" class="btn-ver">
          {{ cargando ? 'Cargando...' : 'Ver reporte' }}
        </button>
        <button @click="descargarPDF" :disabled="descargando" class="btn-pdf">
          {{ descargando ? 'Generando...' : 'Descargar PDF' }}
        </button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <!-- RESULTADOS -->
    <div v-if="reporte" class="resultados">

      <!-- ESTADÍSTICAS -->
      <div class="stats-reporte">
        <div class="stat">
          <span class="stat-valor">{{ reporte.total_registros }}</span>
          <span class="stat-label">Total registros</span>
        </div>
        <div class="stat">
          <span class="stat-valor">{{ reporte.estadisticas.total_entradas }}</span>
          <span class="stat-label">Total entradas</span>
        </div>
        <div class="stat">
          <span class="stat-valor">{{ reporte.estadisticas.puntuales }}</span>
          <span class="stat-label">Puntuales</span>
        </div>
        <div class="stat">
          <span class="stat-valor">{{ reporte.estadisticas.tardanzas }}</span>
          <span class="stat-label">Tardanzas</span>
        </div>
      </div>

      <!-- TABLA -->
      <div class="tabla-container">
        <table class="tabla">
          <thead>
            <tr>
              <th>#</th>
              <th>Trabajador</th>
              <th>DNI</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Fecha y Hora</th>
              <th>Dispositivo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="reporte.marcaciones.length === 0">
              <td colspan="7" class="vacio">No hay marcaciones en este período</td>
            </tr>
            <tr v-for="(m, i) in reporte.marcaciones" :key="m.id">
              <td>{{ i + 1 }}</td>
              <td>{{ m.trabajador_nombre }}</td>
              <td>{{ m.dni }}</td>
              <td>
                <span :class="['badge', m.tipo === 'ENTRADA' ? 'badge-entrada' : 'badge-salida']">
                  {{ m.tipo }}
                </span>
              </td>
              <td>
                <span v-if="m.estado" :class="['badge', m.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']">
                  {{ m.estado }}
                </span>
                <span v-else>—</span>
              </td>
              <td>{{ formatearFechaHora(m.fecha) }}</td>
              <td>{{ m.dispositivo }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const fechaInicio  = ref('')
const fechaFin     = ref('')
const trabajadorId = ref('')
const filtroEstado = ref('todos')   // 'todos' | 'activos' | 'inactivos'
const trabajadores = ref([])        // lista completa (activos + inactivos)
const reporte      = ref(null)
const cargando     = ref(false)
const descargando  = ref(false)
const error        = ref('')

// Lista filtrada según el selector de estado
const trabajadoresFiltrados = computed(() => {
  if (filtroEstado.value === 'activos')   return trabajadores.value.filter(t =>  t.activo)
  if (filtroEstado.value === 'inactivos') return trabajadores.value.filter(t => !t.activo)
  return trabajadores.value
})

// Al cambiar el filtro de estado, resetear el trabajador seleccionado
function onFiltroEstadoCambio() {
  trabajadorId.value = ''
}

onMounted(async () => {
  try {
    // Llamada 1: activos (comportamiento original)
    const resActivos   = await api.get('/api/trabajadores/')
    const listaActivos = resActivos.data.results
      || resActivos.data.trabajadores
      || resActivos.data
      || []

    // Llamada 2: inactivos usando el nuevo parámetro ?activo=false
    let listaInactivos = []
    try {
      const resInactivos = await api.get('/api/trabajadores/?activo=false')
      const raw = resInactivos.data.results
        || resInactivos.data.trabajadores
        || resInactivos.data
        || []
      // Evitar duplicados por si la API devuelve todos en ambas llamadas
      const idsActivos = new Set(listaActivos.map(t => t.id))
      listaInactivos = raw.filter(t => !idsActivos.has(t.id))
    } catch {
      // Si ?activo=false no está soportado aún, solo se muestran activos
    }

    const todos = [...listaActivos, ...listaInactivos]
    trabajadores.value = todos.sort((a, b) =>
      a.apellido_paterno.localeCompare(b.apellido_paterno)
    )
  } catch (e) {
    console.error('Error cargando trabajadores:', e)
  }

  // Fechas por defecto: primer día del mes actual → hoy
  const hoy       = new Date()
  const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  fechaFin.value    = hoy.toISOString().split('T')[0]
  fechaInicio.value = primerDia.toISOString().split('T')[0]
})

// Construye los query params comunes para reporte y PDF
function buildParams() {
  const params = new URLSearchParams({
    fecha_inicio: fechaInicio.value,
    fecha_fin:    fechaFin.value,
  })
  if (trabajadorId.value) {
    // Trabajador específico seleccionado → ignora filtro de estado
    params.append('trabajador_id', trabajadorId.value)
  } else if (filtroEstado.value !== 'todos') {
    // Sin trabajador específico → enviar filtro de estado
    params.append('estado_trabajador', filtroEstado.value)
  }
  return params.toString()
}

async function verReporte() {
  if (!fechaInicio.value || !fechaFin.value) {
    error.value = 'Seleccione fecha inicio y fecha fin'
    return
  }
  error.value    = ''
  cargando.value = true
  try {
    const response = await api.get(`/api/marcaciones/reporte/?${buildParams()}`)
    reporte.value  = response.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al cargar el reporte'
  } finally {
    cargando.value = false
  }
}

async function descargarPDF() {
  if (!fechaInicio.value || !fechaFin.value) {
    error.value = 'Seleccione fecha inicio y fecha fin'
    return
  }
  error.value       = ''
  descargando.value = true
  try {
    const response = await api.get(
      `/api/marcaciones/reporte/pdf/?${buildParams()}`,
      { responseType: 'blob' }
    )
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const link = document.createElement('a')
    link.href     = URL.createObjectURL(blob)
    link.download = `reporte_asistencia_${fechaInicio.value}_${fechaFin.value}.pdf`
    link.click()
    URL.revokeObjectURL(link.href)
  } catch (e) {
    error.value = 'Error al generar el PDF'
  } finally {
    descargando.value = false
  }
}

function formatearFechaHora(fecha) {
  return new Date(fecha).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<style scoped>
.filtros-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}

.filtros-card h3 {
  font-size: 1.45em;
  color: #1a3a6b;
  margin-bottom: 20px;
}

.filtros {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.campo label {
  display: block;
  font-size: 1em;
  font-weight: 600;
  color: #1a3a6b;
  margin-bottom: 4px;
}

.campo input, .campo select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.88rem;
  box-sizing: border-box;
}

.campo input:focus, .campo select:focus {
  outline: none;
  border-color: #1a3a6b;
}

.botones-filtro {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-ver {
  padding: 10px 24px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-ver:hover:not(:disabled) { background: #000000; }

.btn-pdf {
  padding: 10px 24px;
  background: #ff0000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-pdf:hover:not(:disabled) { background: #cc0202; }

.btn-ver:disabled, .btn-pdf:disabled { opacity: 0.7; cursor: not-allowed; }

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  margin-top: 12px;
}

.stats-reporte {
  display: flex;
  gap: 25px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat {
  background: white;
  border-radius: 10px;
  padding: 16px 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  flex: 1;
  min-width: 120px;
  transition: all 0.3s ease;
}

.stat:hover { transform: scale(1.08); background-color: #000; }
.stat:hover .stat-valor, .stat:hover .stat-label { color: #fff; }

.stat-valor { display: block; font-size: 1.9em; font-weight: bold; color: #1a3a6b; }
.stat-label { font-size: 1.02em; color: #666; }

.tabla-container {
  background: white;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.88rem; }

.tabla th {
  background: #1a3a6b;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.tabla td { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; color: #333; }
.tabla tr:hover { background: #f8fafc; }
.vacio { text-align: center; color: #666; padding: 40px !important; }

.badge { padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-entrada  { background: #dbeafe; color: #1d4ed8; }
.badge-salida   { background: #f3f4f6; color: #374151; }
.badge-puntual  { background: #dcfce7; color: #16a34a; }
.badge-tardanza { background: #fef9c3; color: #ca8a04; }
</style>