<!-- MarcacionesView.vue — Marcaciones con vista por período -->
<template>
  <AdminLayout titulo="Marcaciones">

    <div class="toolbar">
      <div>
        <h3>Marcaciones</h3>
        <p class="fecha">{{ fechaHoy }}</p>
      </div>
      <div class="toolbar-right">
        <!-- Tabs de período -->
        <div class="periodo-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.valor"
            :class="['tab-btn', { activo: periodoActivo === tab.valor }]"
            @click="cambiarPeriodo(tab.valor)"
            :disabled="cargando"
          >
            {{ tab.label }}
          </button>
        </div>
        <button @click="cargar" :disabled="cargando" class="btn-actualizar">
          {{ cargando ? '...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <!-- ESTADÍSTICAS rápidas del período -->
    <div class="stats-row" v-if="!cargando && stats">
      <div class="stat-chip">
        <span class="stat-num">{{ stats.total }}</span>
        <span class="stat-lbl">Total</span>
      </div>
      <div class="stat-chip verde">
        <span class="stat-num">{{ stats.entradas }}</span>
        <span class="stat-lbl">Entradas</span>
      </div>
      <div class="stat-chip azul">
        <span class="stat-num">{{ stats.salidas }}</span>
        <span class="stat-lbl">Salidas</span>
      </div>
      <div class="stat-chip amarillo">
        <span class="stat-num">{{ stats.tardanzas }}</span>
        <span class="stat-lbl">Tardanzas</span>
      </div>
      <div class="stat-chip gris">
        <span class="stat-num">{{ stats.puntuales }}</span>
        <span class="stat-lbl">Puntuales</span>
      </div>
    </div>

    <!-- TABLA -->
    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando marcaciones...</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Trabajador</th>
            <th>DNI</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Fecha y Hora</th>
            <th>Dispositivo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="marcaciones.length === 0">
            <td colspan="6" class="vacio">No hay marcaciones en este período</td>
          </tr>
          <tr v-for="m in marcaciones" :key="m.id">
            <td class="td-nombre">{{ m.trabajador_nombre }}</td>
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
              <span v-else class="sin-estado">—</span>
            </td>
            <td class="td-fecha">{{ formatearFechaHora(m.fecha) }}</td>
            <td class="td-dispositivo">{{ m.dispositivo }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pie: total de registros mostrados -->
    <div v-if="!cargando && marcaciones.length > 0" class="pie-tabla">
      {{ marcaciones.length }} registro{{ marcaciones.length !== 1 ? 's' : '' }} encontrado{{ marcaciones.length !== 1 ? 's' : '' }}
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const marcaciones    = ref([])
const cargando       = ref(true)
const periodoActivo  = ref('hoy')

const tabs = [
  { valor: 'hoy',    label: 'Hoy'    },
  { valor: 'semana', label: 'Semana' },
  { valor: 'mes',    label: 'Mes'    },
]

const fechaHoy = computed(() =>
  new Date().toLocaleDateString('es-PE', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric'
  })
)

// Estadísticas calculadas desde las marcaciones cargadas
const stats = computed(() => {
  if (!marcaciones.value.length) return null
  const entradas  = marcaciones.value.filter(m => m.tipo === 'ENTRADA')
  const salidas   = marcaciones.value.filter(m => m.tipo === 'SALIDA')
  return {
    total:     marcaciones.value.length,
    entradas:  entradas.length,
    salidas:   salidas.length,
    puntuales: entradas.filter(m => m.estado === 'PUNTUAL').length,
    tardanzas: entradas.filter(m => m.estado === 'TARDANZA').length,
  }
})

// Calcula las fechas de inicio y fin según el período
function getRango(periodo) {
  const hoy = new Date()
  const toISO = d => d.toLocaleDateString('en-CA')   // YYYY-MM-DD local

  if (periodo === 'hoy') {
    return { inicio: toISO(hoy), fin: toISO(hoy) }
  }

  if (periodo === 'semana') {
    // Lunes de la semana actual
    const lunes = new Date(hoy)
    lunes.setDate(hoy.getDate() - ((hoy.getDay() + 6) % 7))
    return { inicio: toISO(lunes), fin: toISO(hoy) }
  }

  if (periodo === 'mes') {
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    return { inicio: toISO(primerDia), fin: toISO(hoy) }
  }
}

async function cargar() {
  cargando.value = true
  try {
    if (periodoActivo.value === 'hoy') {
      // Usa el endpoint de hoy (más eficiente)
      const res = await api.get('/api/marcaciones/hoy/')
      // El endpoint hoy devuelve marcaciones con campo fecha ya formateado
      marcaciones.value = (res.data.marcaciones || []).slice().reverse()
    } else {
      // Para semana y mes usa el endpoint de reporte
      const { inicio, fin } = getRango(periodoActivo.value)
      const res = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: inicio, fecha_fin: fin }
      })
      marcaciones.value = res.data.marcaciones || []
    }
  } catch (e) {
    console.error('Error cargando marcaciones:', e)
    marcaciones.value = []
  } finally {
    cargando.value = false
  }
}

async function cambiarPeriodo(nuevo) {
  if (periodoActivo.value === nuevo || cargando.value) return
  periodoActivo.value = nuevo
  await cargar()
}

function formatearFechaHora(fecha) {
  return new Date(fecha).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(cargar)
</script>

<style scoped>
/* ── Toolbar ── */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar h3 {
  font-size: 1.45em;
  font-weight: 700;
  color: #1a3a6b;
  margin: 0 0 2px;
}

.fecha {
  font-size: 0.88em;
  color: #666;
  margin: 0;
  text-transform: capitalize;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* ── Tabs de período ── */
.periodo-tabs {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
}

.tab-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.tab-btn:hover:not(:disabled) {
  color: #1a3a6b;
}

.tab-btn.activo {
  background: white;
  color: #1a3a6b;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Botón actualizar ── */
.btn-actualizar {
  background: #08c22a;
  color: white;
  font-size: 0.9em;
  font-weight: 600;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-actualizar:hover:not(:disabled) { background: #4a7ac2; }
.btn-actualizar:disabled { opacity: 0.6; cursor: not-allowed; }

/* ── Stats rápidas ── */
.stats-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat-chip {
  flex: 1;
  min-width: 80px;
  background: white;
  border: 1px solid #e8eaf0;
  border-radius: 10px;
  padding: 12px 16px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-top: 3px solid #94a3b8;
}

.stat-chip.verde  { border-top-color: #10b981; }
.stat-chip.azul   { border-top-color: #3b82f6; }
.stat-chip.amarillo { border-top-color: #f59e0b; }
.stat-chip.gris   { border-top-color: #64748b; }

.stat-num {
  display: block;
  font-size: 1.6rem;
  font-weight: 800;
  color: #111827;
  line-height: 1;
}

.stat-lbl {
  display: block;
  font-size: 0.72rem;
  color: #6b7280;
  font-weight: 500;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

/* ── Tabla ── */
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
  white-space: nowrap;
}

.tabla td {
  padding: 11px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.tabla tr:last-child td { border-bottom: none; }
.tabla tr:hover td { background: #f8fafc; }

.td-nombre {
  font-weight: 600;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-fecha    { white-space: nowrap; color: #4b5563; }
.td-dispositivo { color: #6b7280; font-size: 0.82rem; }

.sin-estado { color: #d1d5db; }

/* ── Badges ── */
.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.76rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-entrada  { background: #dbeafe; color: #1d4ed8; }
.badge-salida   { background: #f3f4f6; color: #374151; }
.badge-puntual  { background: #dcfce7; color: #16a34a; }
.badge-tardanza { background: #fef9c3; color: #ca8a04; }

/* ── Estados ── */
.cargando {
  text-align: center;
  padding: 48px;
  color: #9ca3af;
  font-size: 0.9rem;
}

.vacio {
  text-align: center;
  color: #9ca3af;
  padding: 48px !important;
  font-size: 0.9rem;
}

/* ── Pie ── */
.pie-tabla {
  text-align: right;
  font-size: 0.78rem;
  color: #9ca3af;
  margin-top: 8px;
  padding-right: 4px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-right {
    width: 100%;
    justify-content: space-between;
  }

  .toolbar h3 { font-size: 1.3em; }

  .periodo-tabs { flex: 1; }
  .tab-btn { flex: 1; padding: 6px 8px; font-size: 0.8rem; }

  .btn-actualizar { padding: 8px 14px; font-size: 0.85em; }

  .stats-row { gap: 8px; }
  .stat-chip { min-width: 60px; padding: 10px 8px; }
  .stat-num  { font-size: 1.3rem; }
  .stat-lbl  { font-size: 0.65rem; }

  .tabla th, .tabla td { padding: 10px 10px; font-size: 0.8rem; }
  .td-nombre { max-width: 120px; }
}
</style>