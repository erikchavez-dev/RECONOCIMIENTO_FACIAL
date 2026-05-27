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
            <span class="leg-item"><span class="leg-dot" style="background:#27995f"></span>Puntuales</span>
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
          backgroundColor: '#27995f',
          borderRadius: 3,
          borderSkipped: false,
          barPercentage: 0.7,
          categoryPercentage: 0.6,
        },
        {
          label: 'Tardanzas',
          data: tardanzas,
          backgroundColor: '#f59e0b',
          borderRadius: 3,
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
        backgroundColor: ['#27995f', '#e69200', '#dfdfe4'],
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
          labels: { color: '#000', font: { size: 12, weight: 600 }, padding: 12, }
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
          ctx.fillStyle = pct > 30 ? '#fff' : '#fff'
          ctx.fillText(String(valor), x, y - 7)

          // Porcentaje abajo
          ctx.font      = '10px sans-serif'
          ctx.fillStyle = pct > 30 ? '#000' : '#000'
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

<style scoped src="./style.css"></style>