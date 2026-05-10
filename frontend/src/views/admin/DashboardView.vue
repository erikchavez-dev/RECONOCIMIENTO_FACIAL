<template>
  <AdminLayout titulo="Dashboard">

    <div v-if="cargando" class="cargando">Cargando estadísticas...</div>

    <div v-else class="dash">

    <!-- Bienvenida -->
      <div class="welcome">
        <div>
          <h2 class="welcome-title">Bienvenido, {{nombreAdmin}}</h2>
          <p class="welcome-sub">Panel de control — Municipalidad Provincial de Cajamarca</p>
        </div>
        <div class="welcome-right">
          <span class="badge-fecha">{{ fechaTexto }}</span>
          <button @click="recargar" class="btn-refresh" :disabled="cargando">
            Actualizar
          </button>
        </div>
      </div>

      <!-- Metricas principales -->
      <div class="metrics">
       <div class="mc">
          <div class="mc-body">
            <div class="mc-header">
              <img :src="iconoTrabajadores" alt="trabajadores" class="tarjeta-icono" />
              <span class="mc-label">Trabajadores</span>
            </div>
            <span class="mc-val">{{ stats.trabajadores?.total_activos ?? 0 }}</span>
            <div class="mc-footer">
              <span class="mc-sub neutral">
                <strong>{{ stats.trabajadores?.con_embedding ?? 0 }}</strong> con embedding
              </span>
            </div>
          </div>
        </div>
       <div class="mc">
          <div class="mc-body">
            <div class="mc-header">
              <img :src="iconoEntrada" alt="trabajadores" class="tarjeta-icono" />
              <span class="mc-label">Entradas de hoy</span>
            </div>
            <span class="mc-val">{{ stats.hoy?.entradas ?? 0}}</span>
            <div class="mc-footer">
              <span class="mc-sub neutral">
                <span class="mc-sub up">{{ pctEntradas }}% del total</span>
              </span>
            </div>
          </div>
        </div>
       <div class="mc">
          <div class="mc-body">
            <div class="mc-header">
              <img :src="iconoTardanza" alt="trabajadores" class="tarjeta-icono" />
              <span class="mc-label">Tardanzas</span>
            </div>
            <span class="mc-val">{{ stats.hoy?.tardanzas ?? 0 }}</span>
            <div class="mc-footer">
              <span class="mc-sub neutral">
                <span class="mc-sub up">Hoy</span>
              </span>
            </div>
          </div>
        </div>
       <div class="mc">
          <div class="mc-body">
            <div class="mc-header">
              <img :src="iconoMarcacion" alt="trabajadores" class="tarjeta-icono" />
              <span class="mc-label">Marcaciones</span>
            </div>
            <span class="mc-val">{{ stats.hoy?.sin_marcar ?? 0 }}</span>
            <div class="mc-footer">
              <span class="mc-sub neutral">
                <span class="mc-sub up">Aún no marcaron</span>
              </span>
            </div>
          </div>
        </div>
       <div class="mc">
          <div class="mc-body">
            <div class="mc-header">
              <img :src="iconoSalida" alt="trabajadores" class="tarjeta-icono" />
              <span class="mc-label">Salidas hoy</span>
            </div>
            <span class="mc-val">{{ stats.hoy?.salidas ?? 0 }}</span>
            <div class="mc-footer">
              <span class="mc-sub neutral">
                <span class="mc-sub up">de {{ stats.hoy?.entradas ?? 0 }} entradas</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Gráficos de barras y circular -->
      <div class="charts-row">

        <!-- Gráfico de BARRAS AGRUPADAS -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Asistencia</span>
            <!-- Selector de período -->
            <div class="periodo-tabs">
              <button
                v-for="p in periodos"
                :key="p.valor"
                :class="['tab-periodo', { activo: periodoActivo === p.valor }]"
                @click="cambiarPeriodo(p.valor)"
                :disabled="cargandoGrafico"
              >{{ p.label }}</button>
            </div>
          </div>
          <div class="chart-legend">
            <span class="leg-item"><span class="leg-dot" style="background:#10b981"></span>Puntuales</span>
            <span class="leg-item"><span class="leg-dot" style="background:#f59e0b"></span>Tardanzas</span>
          </div>
          <div class="chart-wrap" style="position:relative; height:200px;">
            <div v-if="cargandoGrafico" class="chart-loading">Cargando datos...</div>
            <canvas ref="barCanvas"></canvas>
          </div>
        </div>

        <!-- Gráfico circular con porcentajes -->
        <div class="card dona-card">
          <div class="card-header">
            <span class="card-title">Puntualidad semanal</span>
          </div>
          <div class="chart-wrap" style="height: 180px;">
            <canvas ref="donaCanvas"></canvas>
          </div>
        </div>

      </div>

      <!-- Últimas marcaciones y mapa -->
      <div class="bottom-row">

        <!-- Últimas marcaciones — más reciente primero -->
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
                <td colspan="4" class="vacio">Aún no hay marcaciones el día de hoy</td>
              </tr>
              <!-- slice invertido: más reciente primero -->
              <tr v-for="m in marcacionesHoyInvertido.slice(0, 8)" :key="m.id">
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
           <div id="mapa-leaflet" class="mapa-leaflet"></div>
            <p class="ubi-marca">Ubicaciones</p>
          </div>
        </div>

      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import iconoTrabajadores from '@/assets/dashboard-trabajadores.svg'
import iconoEntrada from '@/assets/dashboard-entrada.svg'
import iconoTardanza from '@/assets/dashboard-tardanza.svg'
import iconoMarcacion from '@/assets/dashboard-marcacion.svg'
import iconoSalida from '@/assets/dashboard-salida.svg'

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
const cargandoGrafico = ref(false)
const marcacionesHoy  = ref([])
const barCanvas  = ref(null)
let   barChart   = null
const donaCanvas = ref(null)
let   donaChart  = null

// ── Período del gráfico de barras ─────────────────────────
const periodos = [
  { valor: 'semanal',  label: 'Semanal'  },
  { valor: 'mensual',  label: 'Mensual'  },
  { valor: 'anual',    label: 'Anual'    },
]
const periodoActivo = ref('semanal')

// ── Computed: marcaciones en orden invertido (reciente primero) ──
const marcacionesHoyInvertido = computed(() =>
  [...marcacionesHoy.value].reverse()
)

// ── Nombre y fecha ────────────────────────────────────────
const nombreAdmin = computed(() =>
  auth.usuario?.nombre_completo?.split(' ')[0] ||
  auth.usuario?.nombre_completo?.split(' ')[1] || 'Admin'
)
const DIAS  = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado']
const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
const fechaTexto = computed(() => {
  const d = new Date()
  return `${DIAS[d.getDay()]} ${d.getDate()} de ${MESES[d.getMonth()]} del ${d.getFullYear()}`
})
const pctEntradas = computed(() => {
  const total = stats.value.trabajadores?.total_activos || 0
  const ent   = stats.value.hoy?.entradas || 0
  return total > 0 ? Math.round((ent / total) * 100) : 0
})

// ── Carga de estadísticas (sin cambios) ───────────────────
async function cargarEstadisticas() {
  try {
    const r = await api.get('/api/marcaciones/estadisticas/')
    stats.value = r.data
  } catch (e) {
    console.error('Error stats:', e)
  } finally {
    cargando.value = false
    await nextTick()
    construirBarras('semanal')
    construirDona()
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

onMounted(async () => {
  await Promise.all([cargarEstadisticas(), cargarHoy()])
  await nextTick()
  construirBarras('semanal')
  construirDona()
  await nextTick()
  iniciarMapa()
})

// ── Cambiar período ───────────────────────────────────────
async function cambiarPeriodo(nuevo) {
  if (periodoActivo.value === nuevo || cargandoGrafico.value) return
  periodoActivo.value = nuevo
  await construirBarras(nuevo)
}

// ── Helpers de fechas ─────────────────────────────────────
function toLocalISO(d) {
  return d.toLocaleDateString('en-CA')   // YYYY-MM-DD en zona local
}

function rangosSemana() {
  const hoy = new Date()
  const rangos = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(hoy)
    d.setDate(hoy.getDate() - i)
    rangos.push({ label: DIAS[d.getDay()].substring(0, 3), inicio: toLocalISO(d), fin: toLocalISO(d) })
  }
  return rangos
}

function rangosMes() {
  const hoy   = new Date()
  const anio  = hoy.getFullYear()
  const mes   = hoy.getMonth()
  const rangos = []
  // Semanas del mes actual (agrupadas por semana ISO aprox.)
  const primerDia = new Date(anio, mes, 1)
  const ultimoDia = new Date(anio, mes + 1, 0).getDate()
  let diaActual   = 1
  let semana      = 1
  while (diaActual <= ultimoDia) {
    const finSemana = Math.min(diaActual + 6, ultimoDia)
    const inicio    = toLocalISO(new Date(anio, mes, diaActual))
    const fin       = toLocalISO(new Date(anio, mes, finSemana))
    rangos.push({ label: `S${semana}`, inicio, fin })
    diaActual += 7
    semana++
  }
  return rangos
}

function rangosAnio() {
  const anio   = new Date().getFullYear()
  const mesesLabel = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
  return mesesLabel.map((label, i) => {
    const ultimo = new Date(anio, i + 1, 0).getDate()
    return {
      label,
      inicio: toLocalISO(new Date(anio, i, 1)),
      fin:    toLocalISO(new Date(anio, i, ultimo)),
    }
  })
}

// ── Construir gráfico de BARRAS AGRUPADAS ─────────────────
async function construirBarras(periodo) {
  if (!barCanvas.value) return
  cargandoGrafico.value = true

  let rangos = []
  if (periodo === 'semanal') rangos = rangosSemana()
  else if (periodo === 'mensual') rangos = rangosMes()
  else rangos = rangosAnio()

  const labels    = []
  const puntuales = []
  const tardanzas = []

  for (const rango of rangos) {
    labels.push(rango.label)
    try {
      const r = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: rango.inicio, fecha_fin: rango.fin }
      })
      const est = r.data.estadisticas || {}
      puntuales.push(est.puntuales  || 0)
      tardanzas.push(est.tardanzas  || 0)
    } catch {
      puntuales.push(0)
      tardanzas.push(0)
    }
  }

  if (barChart) barChart.destroy()

  barChart = new Chart(barCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Puntuales',
          data: puntuales,
          backgroundColor: '#10b981',
          borderRadius: 5,
          borderSkipped: false,
          barPercentage: 0.7,
          categoryPercentage: 0.6,
        },
        {
          label: 'Tardanzas',
          data: tardanzas,
          backgroundColor: '#f59e0b',
          borderRadius: 5,
          borderSkipped: false,
          barPercentage: 0.7,
          categoryPercentage: 0.6,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            title: ctx => `${ctx[0].label}`,
          }
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { size: 11 } },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: { color: '#94a3b8', font: { size: 11 }, stepSize: 1, precision: 0 },
          grid: { color: 'rgba(0,0,0,0.04)' },
        }
      }
    }
  })

  cargandoGrafico.value = false
}

// ── Gráfico circular con número y porcentaje ──────────────
async function construirDona() {
  if (!donaCanvas.value) return

  const hoy = new Date()
  let puntuales = 0, tardanzas = 0, sinMarcar = 0

  for (let i = 6; i >= 0; i--) {
    const d = new Date(hoy)
    d.setDate(hoy.getDate() - i)
    const fechaStr = toLocalISO(d)
    try {
      const r      = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: fechaStr, fecha_fin: fechaStr }
      })
      const est = r.data.estadisticas || {}
      puntuales += est.puntuales || 0
      tardanzas += est.tardanzas || 0
      const total = est.total_entradas || 0
      sinMarcar  += Math.max(0, total - (est.puntuales || 0) - (est.tardanzas || 0))
    } catch {
      // ignorar
    }
  }

  const totalDona = puntuales + tardanzas + sinMarcar

  if (donaChart) donaChart.destroy()

  donaChart = new Chart(donaCanvas.value, {
    type: 'doughnut',
    data: {
      labels: ['Puntuales', 'Tardanzas', 'Sin marcar'],
      datasets: [{
        data: [puntuales, tardanzas, sinMarcar],
        backgroundColor: ['#10b981', '#f59e0b', '#dfdfe4'],
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 10,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#64748b', font: { size: 11 }, padding: 12 }
        },
        tooltip: {
          callbacks: {
            label: ctx => {
              const val = ctx.raw
              const pct = totalDona > 0 ? Math.round((val / totalDona) * 100) : 0
              return ` ${ctx.label}: ${val} (${pct}%)`
            }
          }
        },
        // Plugin inline para mostrar número y % dentro de cada segmento
        datalabels: false,   // por si chart.js-datalabels no está, usamos plugin custom
      },
    },
    // Plugin personalizado que dibuja el número y porcentaje dentro de cada segmento
    plugins: [{
      
      id: 'donaLabels',
      afterDraw(chart) {
        const { ctx, data } = chart
        const total = data.datasets[0].data.reduce((a, b) => a + b, 0)
        if (total === 0) return

        chart.getDatasetMeta(0).data.forEach((arc, i) => {
          const valor = data.datasets[0].data[i]
          if (valor === 0) return
          const pct = Math.round((valor / total) * 100)

          // Posición central del segmento
          const cx     = arc.x
          const cy     = arc.y
          const angle  = (arc.startAngle + arc.endAngle) / 2
          const radio  = (arc.innerRadius + arc.outerRadius) / 2

          const x = cx + Math.cos(angle) * radio
          const y = cy + Math.sin(angle) * radio

          // Solo dibujar si el segmento tiene suficiente espacio (> 5%)
          if (pct < 5) return

          ctx.save()
          ctx.textAlign    = 'center'
          ctx.textBaseline = 'middle'

          // Número arriba
          ctx.font      = 'bold 11px sans-serif'
          ctx.fillStyle = pct > 30 ? '#fff' : '#374151'
          ctx.fillText(String(valor), x, y - 7)

          // Porcentaje abajo
          ctx.font      = '10px sans-serif'
          ctx.fillStyle = pct > 30 ? 'rgba(255,255,255,0.85)' : '#6b7280'
          ctx.fillText(`${pct}%`, x, y + 7)

          ctx.restore()
        })
      }
    }]
  })
}

// ── Mapa (sin cambios) ────────────────────────────────────
const marcacionesConGeo = computed(() =>
  marcacionesHoy.value.filter(m => m.latitud && m.longitud).length
)

function iniciarMapa() {
  const contenedor = document.getElementById('mapa-leaflet')
  if (!contenedor) return

  if (!window.L) {
    const link    = document.createElement('link')
    link.rel      = 'stylesheet'
    link.href     = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    document.head.appendChild(link)

    const script  = document.createElement('script')
    script.src    = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.onload = () => renderizarMapa(contenedor)
    document.head.appendChild(script)
  } else {
    renderizarMapa(contenedor)
  }
}

function renderizarMapa(contenedor) {
  const L = window.L
  if (contenedor._leaflet_id) { contenedor._leaflet_id = null; contenedor.innerHTML = '' }

  const mapa = L.map(contenedor).setView([-7.1518, -78.5117], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapa)

  const conGeo = marcacionesHoy.value.filter(m => m.latitud && m.longitud)

  if (conGeo.length === 0) {
    marcacionesHoy.value.forEach(m => {
      const lat    = -7.1626 + (Math.random() * 0.01)
      const lng    = -78.5001 + (Math.random() * 0.01)
      const marker = L.marker([lat, lng]).addTo(mapa)
      marker.bindPopup(`<b>${m.trabajador_nombre}</b><br>${m.tipo} — ${m.estado || ''}<br>${formatHora(m.fecha)}`)
      marker.bindTooltip(m.trabajador_nombre, { direction: 'top', offset: [0, -10] })
    })
    return
  }

  conGeo.forEach(m => {
    const lat = parseFloat(m.latitud)
    const lng = parseFloat(m.longitud)
    L.marker([lat, lng]).addTo(mapa)
      .bindPopup(`<b>${m.trabajador_nombre}</b><br>${m.tipo} — ${m.estado || ''}<br>${formatHora(m.fecha)}`)
  })
}

async function recargar() {
  cargando.value    = true
  cargandoHoy.value = true
  await Promise.all([cargarEstadisticas(), cargarHoy()])
}

function formatHora(fecha) {
  return new Date(fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* ── Layout ── */
.dash { display: flex; flex-direction: column; gap: 14px; }
.cargando { text-align: center; color: #666; padding: 40px; }

/* ── Bienvenida ── */
.welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.welcome-title {
  font-size: 1.7em;
  font-weight: 700;
  color: #1a3a6b;
}

.welcome-sub {
  font-size: 1.03em;
  color: #64748b;
  margin-top: 2px;
}

.welcome-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.badge-fecha {
  font-size: 1.05em;
  font-weight: 600;
  color: #1a3a6b;
  background: #f1f5f9;
  padding: 5px 12px;
}

.btn-refresh {
  background: #1a3a6b;
  color: #fff;
  font-size: 1.01em;
  font-weight: 600;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #000000;
  color: #ffffff;
}

.btn-refresh:disabled {
  opacity: 0.6;
}

/* ── Métricas ── */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
.mc { background: #fff; border-radius: 16px; border: 1px solid #f0f0f0; transition: all 0.2s ease; padding: 20px; }
.mc:hover { transform: translateY(-8px); background: #000; border-radius: 16px; border: 1px solid #f0f0f0; }
.mc-label { font-size: 1.03em; font-weight: 500; color: #000; }
.mc-val { display: block; font-size: 1.7rem; font-weight: 700; color: #111827; margin-bottom: 8px; }
.mc-sub { font-size: 0.9em !important; display: flex; align-items: center; gap: 4px; }
.mc:hover .mc-label, .mc:hover .mc-val, .mc:hover .mc-footer { color: #fff !important; }
.mc-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.tarjeta-icono { width: 34px; height: 34px; padding: 8px; background: #dfdfe4; border-radius: 8px; object-fit: contain; }

/* ── Cards ── */
.card { background: #fff; border-radius: 12px; border: 1px solid #e8eaf0; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.card-title { font-size: 1.031em; font-weight: 600; color: #000; }
.card-sub { font-size: 0.75rem; color: #9ca3af; }

/* ── Selector de período ── */
.periodo-tabs {
  display: flex;
  gap: 4px;
}

.tab-periodo {
  padding: 7px 19px;
  margin-left: 8px;
  border-radius: 6px;
  background: #dfdfe4;
  border: 0px;
  color: #000000;
  font-size: 0.95em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.tab-periodo:hover:not(:disabled) {
  background: #000000;
  color: #ffffff;
}

.tab-periodo.activo {
  background: #059462;
  color: #fff;
}

.tab-periodo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
/* ── Gráficos ── */
.charts-row { display: grid; grid-template-columns: 1fr 280px; gap: 12px; }
@media (max-width: 700px) { .charts-row { grid-template-columns: 1fr; } }

.chart-legend { display: flex; gap: 14px; margin-bottom: 10px; flex-wrap: wrap; }
.leg-item { display: flex; align-items: center; gap: 5px; font-size: 0.85em; color: #64748b; }
.leg-dot { width: 12px; height: 12px; border-radius: 50px; flex-shrink: 0; }

.chart-wrap { position: relative; height: 180px; }
.chart-loading {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.8); font-size: 0.82rem; color: #94a3b8; border-radius: 8px; z-index: 2;
}

/* ── Gráfico dona ── */
.dona-card .dona-wrap { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }

/* ── Fila inferior ── */
.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .bottom-row { grid-template-columns: 1fr; } }

/* ── Tabla marcaciones ── */
.act-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.act-table th { font-size: 1.05em; font-weight: 600; color: #0b50d0; padding: 6px 8px; border-bottom: 1px solid #f0f2f5; text-align: left; }
.act-table td { padding: 8px 8px; border-bottom: 1px solid #f8fafc; color: #374151; }
.act-table tr:last-child td { border-bottom: none; }
.act-table tr:hover td { background: #f8fafc; }
.td-nombre { max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 1.02em; }
.vacio { font-size: 1.1em; text-align: center; color: #9ca3af; padding: 20px !important; }

/* ── Pills ── */
.pill { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
.pill-p { background: #16a363; color: #fff; }
.pill-t { background: #f58300; color: #000; }
.pill-s { background: #0e1ce6; color: #fff; }

/* ── Mapa ── */
.mapa-container { display: flex; flex-direction: column; gap: 8px; }
.mapa-leaflet { width: 100%; height: 220px; border-radius: 8px; border: 1px solid #e2e8f0; }
.mapa-info { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #64748b; }
.ubi-marca p { font-size: 1.05em; }

/* ── Cargando mini ── */
.mini-cargando { text-align: center; color: #9ca3af; font-size: 0.82rem; padding: 20px; }
</style>