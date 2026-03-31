<template>
  <AdminLayout titulo="Dashboard">

    <div v-if="cargando" class="cargando">Cargando estadísticas...</div>

    <div v-else class="dash">

      <!-- ── BIENVENIDA ── -->
      <div class="welcome">
        <div>
          <h2 class="welcome-title">Bienvenido, {{ nombreAdmin }}</h2>
          <p class="welcome-sub">Panel de control — Municipalidad Provincial de Cajamarca</p>
        </div>
        <div class="welcome-right">
          <span class="badge-fecha">{{ fechaTexto }}</span>
          <button @click="recargar" class="btn-refresh" :disabled="cargando">
            Actualizar
          </button>
        </div>
      </div>

      <!-- ── MÉTRICAS PRINCIPALES ── -->
      <div class="metrics">
        <div class="mc" style="--accent:#1a3a6b">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Trabajadores</span>
            <span class="mc-val">{{ stats.trabajadores?.total_activos ?? 0 }}</span>
            <span class="mc-sub neutral">{{ stats.trabajadores?.con_embedding ?? 0 }} con embedding</span>
          </div>
        </div>
        <div class="mc" style="--accent:#16a34a">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Entradas hoy</span>
            <span class="mc-val">{{ stats.hoy?.entradas ?? 0 }}</span>
            <span class="mc-sub up">{{ pctEntradas }}% del total</span>
          </div>
        </div>
        <div class="mc" style="--accent:#22c55e">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Puntuales</span>
            <span class="mc-val">{{ stats.hoy?.puntuales ?? 0 }}</span>
            <span class="mc-sub up">{{ pctPuntuales }}% de entradas</span>
          </div>
        </div>
        <div class="mc" style="--accent:#f59e0b">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Tardanzas</span>
            <span class="mc-val">{{ stats.hoy?.tardanzas ?? 0 }}</span>
            <span class="mc-sub warn">hoy</span>
          </div>
        </div>
        <div class="mc" style="--accent:#ef4444">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Sin marcar</span>
            <span class="mc-val">{{ stats.hoy?.sin_marcar ?? 0 }}</span>
            <span class="mc-sub neutral">aún no marcaron</span>
          </div>
        </div>
        <div class="mc" style="--accent:#6366f1">
          <div class="mc-bar"></div>
          <div class="mc-body">
            <span class="mc-label">Salidas hoy</span>
            <span class="mc-val">{{ stats.hoy?.salidas ?? 0 }}</span>
            <span class="mc-sub neutral">de {{ stats.hoy?.entradas ?? 0 }} entradas</span>
          </div>
        </div>
      </div>

      <!-- ── FILA: BARRAS + DONA ── -->
      <div class="charts-row">

        <!-- Gráfico de barras semanal -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Asistencia esta semana</span>
          </div>
          <div class="chart-legend">
            <span class="leg-item"><span class="leg-dot" style="background:#1a3a6b"></span>Puntuales</span>
            <span class="leg-item"><span class="leg-dot" style="background:#f59e0b"></span>Tardanzas</span>
            <span class="leg-item"><span class="leg-dot" style="background:#e5e7eb"></span>Sin marcar</span>
          </div>
          <div class="chart-wrap">
            <canvas ref="barCanvas"></canvas>
          </div>
        </div>

        <!-- Gráfico de dona -->
        <div class="card dona-card">
          <div class="card-header">
            <span class="card-title">Puntualidad del mes</span>
            <span class="card-sub">{{ stats.mes_actual?.mes }}</span>
          </div>
          <div class="dona-wrap">
            <svg class="dona-svg" viewBox="0 0 130 130">
              <circle cx="65" cy="65" r="48" fill="none" stroke="#e5e7eb" stroke-width="18"/>
              <circle
                cx="65" cy="65" r="48"
                fill="none" stroke="#22c55e" stroke-width="18"
                :stroke-dasharray="`${301.59 * (stats.mes_actual?.porcentaje_puntualidad || 0) / 100} 301.59`"
                stroke-linecap="round"
                transform="rotate(-90 65 65)"
              />
              <text x="65" y="61" text-anchor="middle" font-size="19" font-weight="500" fill="#1a3a6b">
                {{ stats.mes_actual?.porcentaje_puntualidad || 0 }}%
              </text>
              <text x="65" y="76" text-anchor="middle" font-size="9" fill="#888">puntual</text>
            </svg>
            <div class="dona-legend">
              <div class="dl-item"><span class="dl-dot" style="background:#22c55e"></span>Puntual {{ stats.mes_actual?.puntuales }}</div>
              <div class="dl-item"><span class="dl-dot" style="background:#f59e0b"></span>Tardanza {{ stats.mes_actual?.tardanzas }}</div>
              <div class="dl-item"><span class="dl-dot" style="background:#e5e7eb"></span>Total {{ stats.mes_actual?.total_entradas }}</div>
            </div>
          </div>
        </div>

      </div>

      <!-- ── FILA: ACTIVIDAD + MAPA ── -->
      <div class="bottom-row">

        <!-- Últimas marcaciones -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Últimas marcaciones</span>
            <span class="card-sub">Hoy</span>
          </div>
          <div v-if="cargandoHoy" class="mini-cargando">Cargando...</div>
          <table v-else class="act-table">
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>Hora</th>
                <th>Tipo</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="marcacionesHoy.length === 0">
                <td colspan="4" class="vacio">Sin marcaciones hoy</td>
              </tr>
              <tr v-for="m in marcacionesHoy.slice(0, 8)" :key="m.id">
                <td class="td-nombre">{{ m.trabajador_nombre }}</td>
                <td>{{ formatHora(m.fecha) }}</td>
                <td>{{ m.tipo === 'ENTRADA' ? 'Entrada' : 'Salida' }}</td>
                <td>
                  <span v-if="m.estado" class="pill" :class="m.estado === 'PUNTUAL' ? 'pill-p' : 'pill-t'">
                    {{ m.estado === 'PUNTUAL' ? 'Puntual' : 'Tardanza' }}
                  </span>
                  <span v-else class="pill pill-s">Salida</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mapa de ubicaciones -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Ubicaciones de marcación</span>
            <span class="card-sub">Hoy — GPS activo</span>
          </div>
          <div class="mapa-container">
            <svg ref="mapaSvg" class="mapa-svg" viewBox="0 0 300 200">
              <!-- Fondo -->
              <rect width="300" height="200" fill="#dbeafe" rx="6"/>
              <!-- Grid calles -->
              <line v-for="y in [40,80,120,160]" :key="'h'+y" x1="0" :y1="y" x2="300" :y2="y" stroke="rgba(255,255,255,0.6)" stroke-width="1"/>
              <line v-for="x in [60,120,180,240]" :key="'v'+x" :x1="x" y1="0" :x2="x" y2="200" stroke="rgba(255,255,255,0.6)" stroke-width="1"/>
              <!-- Puntos de marcación -->
              <g v-for="punto in puntosMapaFiltrados" :key="punto.id">
                <circle :cx="punto.px" :cy="punto.py" :r="punto.r + 6" fill="#1a3a6b" opacity="0.12"/>
                <circle :cx="punto.px" :cy="punto.py" r="6" fill="#1a3a6b" opacity="0.9"/>
                <text :x="punto.px" :y="punto.py - 10" text-anchor="middle" font-size="8" fill="#1e3a6e" font-weight="500">
                  {{ punto.label }}
                </text>
                <text :x="punto.px + 10" :y="punto.py + 4" font-size="8" fill="#1a3a6b">
                  {{ punto.count }}
                </text>
              </g>
              <!-- Label ciudad -->
              <text x="150" y="192" text-anchor="middle" font-size="9" fill="#64748b">Cajamarca, Perú</text>
            </svg>
            <p class="mapa-info">
              <span class="dot-azul"></span>
              {{ marcacionesConGeo }} marcaciones con ubicación GPS hoy
            </p>
          </div>
        </div>

      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import iconoTrabajadores from '@/assets/icono-trabajadores.svg'
import { ref, computed, onMounted, nextTick } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const auth   = useAuthStore()
const stats  = ref({})
const cargando     = ref(true)
const cargandoHoy  = ref(true)
const marcacionesHoy = ref([])
const barCanvas  = ref(null)
let   barChart   = null

// ── Nombre del admin ────────────────────────────────────────
const nombreAdmin = computed(() => auth.usuario?.nombre_completo?.split(' ')[0] || 'Admin')

// ── Fecha legible ───────────────────────────────────────────
const DIAS   = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado']
const MESES  = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
const fechaTexto = computed(() => {
  const d = new Date()
  return `${DIAS[d.getDay()]} ${d.getDate()} de ${MESES[d.getMonth()]} de ${d.getFullYear()}`
})

// ── Porcentajes calculados ──────────────────────────────────
const pctEntradas = computed(() => {
  const total = stats.value.trabajadores?.total_activos || 0
  const ent   = stats.value.hoy?.entradas || 0
  return total > 0 ? Math.round((ent / total) * 100) : 0
})
const pctPuntuales = computed(() => {
  const ent = stats.value.hoy?.entradas || 0
  const pun = stats.value.hoy?.puntuales || 0
  return ent > 0 ? Math.round((pun / ent) * 100) : 0
})

// ── Marcaciones con geo ─────────────────────────────────────
const marcacionesConGeo = computed(() =>
  marcacionesHoy.value.filter(m => m.latitud && m.longitud).length
)

// ── Puntos del mapa ─────────────────────────────────────────
// Agrupa marcaciones por ciudad y las ubica en posiciones relativas dentro del SVG (300x200)
const puntosMapaFiltrados = computed(() => {
  const conGeo = marcacionesHoy.value.filter(m => m.latitud && m.longitud)
  if (conGeo.length === 0) {
    // Sin datos reales → punto fijo en el centro (Municipalidad)
    return [{ id: 1, px: 150, py: 100, r: 8, label: 'Municipalidad', count: marcacionesHoy.value.length }]
  }

  // Agrupar por ciudad
  const ciudades = {}
  conGeo.forEach(m => {
    const key = m.ciudad || `${Number(m.latitud).toFixed(2)},${Number(m.longitud).toFixed(2)}`
    if (!ciudades[key]) ciudades[key] = { count: 0, lat: Number(m.latitud), lng: Number(m.longitud), label: m.ciudad || 'Oficina' }
    ciudades[key].count++
  })

  // Proyectar lat/lng a coordenadas SVG (área Cajamarca aprox)
  const LAT_MIN = -7.25, LAT_MAX = -7.10
  const LNG_MIN = -78.55, LNG_MAX = -78.45
  const SVG_W = 280, SVG_H = 180, PAD = 10

  return Object.entries(ciudades).map(([key, c], i) => {
    let px = PAD + ((c.lng - LNG_MIN) / (LNG_MAX - LNG_MIN)) * SVG_W
    let py = PAD + ((LAT_MAX - c.lat) / (LAT_MAX - LAT_MIN)) * SVG_H
    // Fallback si está fuera del rango
    if (isNaN(px) || px < PAD || px > SVG_W + PAD) px = 80 + i * 60
    if (isNaN(py) || py < PAD || py > SVG_H + PAD) py = 80 + i * 30
    return { id: key, px: Math.round(px), py: Math.round(py), r: Math.min(c.count * 2, 12), label: c.label, count: c.count }
  })
})

// ── Carga de datos ──────────────────────────────────────────
onMounted(async () => {
  await Promise.all([cargarEstadisticas(), cargarHoy()])
})

async function recargar() {
  cargando.value = true
  cargandoHoy.value = true
  await Promise.all([cargarEstadisticas(), cargarHoy()])
}

async function cargarEstadisticas() {
  try {
    const r = await api.get('/api/marcaciones/estadisticas/')
    stats.value = r.data
  } catch (e) {
    console.error('Error stats:', e)
  } finally {
    cargando.value = false
    await nextTick()
    construirBarras()
  }
}

async function cargarHoy() {
  try {
    const r = await api.get('/api/marcaciones/hoy/')
    marcacionesHoy.value = r.data.marcaciones || []
  } catch (e) {
    console.error('Error hoy:', e)
  } finally {
    cargandoHoy.value = false
  }
}

// ── Gráfico de barras ───────────────────────────────────────
function construirBarras() {
  if (!barCanvas.value) return
  const total = stats.value.trabajadores?.total_activos || 48

  // Datos simulados de la semana — reemplaza con endpoint real si tienes histórico semanal
  const dias  = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']
  const pun   = [28, 26, 30, 25, stats.value.hoy?.puntuales || 0]
  const tard  = [5,  7,  4,  9,  stats.value.hoy?.tardanzas || 0]
  const sinM  = pun.map((p, i) => Math.max(0, total - p - tard[i]))

  if (barChart) barChart.destroy()
  barChart = new Chart(barCanvas.value, {
    type: 'bar',
    data: {
      labels: dias,
      datasets: [
        { label: 'Puntuales', data: pun,  backgroundColor: '#1a3a6b', borderRadius: 4, borderSkipped: false },
        { label: 'Tardanzas', data: tard, backgroundColor: '#f59e0b', borderRadius: 4, borderSkipped: false },
        { label: 'Sin marcar',data: sinM, backgroundColor: '#e5e7eb', borderRadius: 4, borderSkipped: false },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { mode: 'index' } },
      scales: {
        x: { stacked: true, ticks: { color: '#888', font: { size: 11 } }, grid: { display: false } },
        y: { stacked: true, beginAtZero: true, ticks: { color: '#888', font: { size: 11 } }, grid: { color: 'rgba(0,0,0,0.05)' } }
      }
    }
  })
}

// ── Helpers ─────────────────────────────────────────────────
function formatHora(fecha) {
  return new Date(fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* ── Layout ── */
.dash { display: flex; flex-direction: column; gap: 14px; }
.cargando { text-align: center; color: #666; padding: 40px; }

/* ── Bienvenida ── */
.welcome { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.welcome-title { font-size: 1.1rem; font-weight: 600; color: #1a3a6b; }
.welcome-sub   { font-size: 0.8rem; color: #64748b; margin-top: 2px; }
.welcome-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.badge-fecha   { font-size: 0.75rem; color: #64748b; background: #f1f5f9; padding: 5px 12px; border-radius: 20px; border: 1px solid #e2e8f0; }
.btn-refresh   { font-size: 0.75rem; padding: 5px 14px; border-radius: 8px; border: 1px solid #d0d5dd; background: #fff; color: #374151; cursor: pointer; }
.btn-refresh:hover { background: #f8fafc; }
.btn-refresh:disabled { opacity: 0.6; }

/* ── Métricas ── */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
.mc {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8eaf0;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
  cursor: default;
}
.mc:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.mc-bar { height: 4px; background: var(--accent); }
.mc-body { padding: 14px 16px; display: flex; flex-direction: column; }
.mc-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.4px; color: #64748b; }
.mc-val   { font-size: 1.7rem; font-weight: 600; color: #111827; margin: 4px 0 2px; line-height: 1; }
.mc-sub   { font-size: 0.72rem; }
.mc-sub.up      { color: #16a34a; }
.mc-sub.warn    { color: #ca8a04; }
.mc-sub.neutral { color: #64748b; }

/* ── Cards genéricas ── */
.card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8eaf0;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
.card-title  { font-size: 0.88rem; font-weight: 600; color: #1a3a6b; }
.card-sub    { font-size: 0.75rem; color: #9ca3af; }

/* ── Gráficos fila ── */
.charts-row { display: grid; grid-template-columns: 1fr 280px; gap: 12px; }
@media (max-width: 700px) { .charts-row { grid-template-columns: 1fr; } }

.chart-legend { display: flex; gap: 14px; margin-bottom: 10px; flex-wrap: wrap; }
.leg-item     { display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: #64748b; }
.leg-dot      { width: 10px; height: 10px; border-radius: 2px; flex-shrink: 0; }
.chart-wrap   { position: relative; height: 180px; }

/* ── Dona ── */
.dona-card .dona-wrap { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.dona-svg    { width: 120px; height: 120px; flex-shrink: 0; }
.dona-legend { display: flex; flex-direction: column; gap: 8px; }
.dl-item     { display: flex; align-items: center; gap: 7px; font-size: 0.75rem; color: #64748b; }
.dl-dot      { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── Fila inferior ── */
.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .bottom-row { grid-template-columns: 1fr; } }

/* ── Tabla actividad ── */
.act-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.act-table th {
  font-size: 0.72rem; font-weight: 600; color: #64748b;
  padding: 6px 8px; border-bottom: 1px solid #f0f2f5; text-align: left;
}
.act-table td { padding: 8px 8px; border-bottom: 1px solid #f8fafc; color: #374151; }
.act-table tr:last-child td { border-bottom: none; }
.act-table tr:hover td { background: #f8fafc; }
.td-nombre { max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.vacio { text-align: center; color: #9ca3af; padding: 20px !important; }

/* ── Pills ── */
.pill   { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
.pill-p { background: #dcfce7; color: #166534; }
.pill-t { background: #fef9c3; color: #854d0e; }
.pill-s { background: #e0e7ff; color: #3730a3; }

/* ── Mapa ── */
.mapa-container { display: flex; flex-direction: column; gap: 8px; }
.mapa-svg  { width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; }
.mapa-info { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #64748b; }
.dot-azul  { width: 8px; height: 8px; border-radius: 50%; background: #1a3a6b; flex-shrink: 0; display: inline-block; }

/* ── Cargando mini ── */
.mini-cargando { text-align: center; color: #9ca3af; font-size: 0.82rem; padding: 20px; }
</style>