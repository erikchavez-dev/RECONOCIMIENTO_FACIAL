<!-- ReportesView.vue — Reportes de asistencia por rango de fechas -->
<!-- Filtros: fecha inicio, fecha fin, trabajador opcional -->
<!-- Botones: Ver reporte y Descargar PDF -->

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
        <div class="campo">
          <label>Trabajador (opcional)</label>
          <select v-model="trabajadorId">
            <option value="">Todos los trabajadores</option>
            <option v-for="t in trabajadores" :key="t.id" :value="t.id">
              {{ t.nombres }} {{ t.apellido_paterno }} — {{ t.dni }}
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
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const fechaInicio = ref('')
const fechaFin = ref('')
const trabajadorId = ref('')
const trabajadores = ref([])
const reporte = ref(null)
const cargando = ref(false)
const descargando = ref(false)
const error = ref('')

onMounted(async () => {
  // Cargar lista de trabajadores para el filtro
  try {
    const response = await api.get('/api/trabajadores/')
    trabajadores.value = response.data
  } catch (e) {
    console.error('Error cargando trabajadores:', e)
  }

  // Fecha por defecto: primer día del mes actual hasta hoy
  const hoy = new Date()
  const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  fechaFin.value = hoy.toISOString().split('T')[0]
  fechaInicio.value = primerDia.toISOString().split('T')[0]
})

async function verReporte() {
  if (!fechaInicio.value || !fechaFin.value) {
    error.value = 'Seleccione fecha inicio y fecha fin'
    return
  }
  error.value = ''
  cargando.value = true
  try {
    let url = `/api/marcaciones/reporte/?fecha_inicio=${fechaInicio.value}&fecha_fin=${fechaFin.value}`
    if (trabajadorId.value) url += `&trabajador_id=${trabajadorId.value}`
    const response = await api.get(url)
    reporte.value = response.data
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
  error.value = ''
  descargando.value = true
  try {
    let url = `/api/marcaciones/reporte/pdf/?fecha_inicio=${fechaInicio.value}&fecha_fin=${fechaFin.value}`
    if (trabajadorId.value) url += `&trabajador_id=${trabajadorId.value}`

    const response = await api.get(url, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
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

.btn-ver:hover:not(:disabled) { background: #142d54; }

.btn-pdf {
  padding: 10px 24px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-pdf:hover:not(:disabled) { background: #b91c1c; }

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
.stats-reporte:hover {
  display: flex;
  gap: 25px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      border-left 0.3s ease,
      box-shadow 0.3s ease;
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

.stat:hover {
  transform: scale(1.08);
  background-color: #000000;
}
.stat:hover .stat-valor,
.stat:hover .stat-label {
  color: #fff;
}


.stat-valor {
  display: block;
  font-size: 1.9em;
  font-weight: bold;
  color: #1a3a6b;
}

.stat-label {
  font-size: 1.02em;
  color: #666;
}

.tabla-container {
  background: white;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.tabla th {
  background: #1a3a6b;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.tabla td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.tabla tr:hover { background: #f8fafc; }

.vacio {
  text-align: center;
  color: #666;
  padding: 40px !important;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}

.badge-entrada { background: #dbeafe; color: #1d4ed8; }
.badge-salida { background: #f3f4f6; color: #374151; }
.badge-puntual { background: #dcfce7; color: #16a34a; }
.badge-tardanza { background: #fef9c3; color: #ca8a04; }
</style>