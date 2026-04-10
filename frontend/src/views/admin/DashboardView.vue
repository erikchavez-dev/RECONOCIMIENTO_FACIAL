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



      <!-- Gráficos de linea y circular -->
      <div class="charts-row">

        <!-- Gráfico de linea -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Asistencia esta semana</span>
          </div>
          <div class="chart-legend">
            <span class="leg-item"><span class="leg-dot" style="background:#10b981"></span>Puntuales</span>
            <span class="leg-item"><span class="leg-dot" style="background:#f59e0b"></span>Tardanzas</span>
            <span class="leg-item"><span class="leg-dot" style="background:#94a3b8"></span>Sin marcar</span>
          </div>
          <div class="chart-wrap">
            <canvas ref="lineCanvas"></canvas>
          </div>
        </div>

       <!-- Gráfico circular semanal -->
        <div class="card dona-card">
          <div class="card-header">
            <span class="card-title">Puntualidad semanal</span>
          </div>
          <div class="chart-wrap" style="height: 180px;">
            <canvas ref="donaCanvas"></canvas>
          </div>
        </div>

      </div>

      <!-- Últimas marcaciones y mapa de donde se marco-->
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
                <td colspan="4" class="vacio">Aú no hay marcaciones el día de hoy</td>
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
const marcacionesHoy = ref([])
const lineCanvas  = ref(null)
let   lineChart   = null
const donaCanvas = ref(null)
let donaChart = null

// Nombre del admin
const nombreAdmin = computed(() => auth.usuario?.nombre_completo?.split(' ')[0] || auth.usuario?.nombre_completo?.split(' ')[1] || 'Admin')

// Fecha legible
const DIAS   = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado']
const MESES  = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
const fechaTexto = computed(() => {
  const d = new Date()
  return `${DIAS[d.getDay()]} ${d.getDate()} de ${MESES[d.getMonth()]} del ${d.getFullYear()}`
})

// para las entradas de hoy en porcentaje
const pctEntradas = computed(() => {
  const total = stats.value.trabajadores?.total_activos || 0
  const ent   = stats.value.hoy?.entradas || 0
  return total > 0 ? Math.round((ent / total) * 100) : 0
})

//para cagar los datos
async function cargarEstadisticas() {
  try {
    const r = await api.get('/api/marcaciones/estadisticas/')
    stats.value = r.data
  } catch (e) {
    console.error('Error stats:', e)
  } finally {
    cargando.value = false
    await nextTick()
    construirLineas()
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


//para el grafico
onMounted(async () => {
  await Promise.all([
    cargarEstadisticas(),
    cargarHoy()
  ])
  await nextTick()
  construirLineas()  
  construirDona()   
  await nextTick()
  iniciarMapa()
})


//funcion para el gráfico circular 
async function construirDona() {
  if (!donaCanvas.value) return

  // Totales semanales: sumar puntuales, tardanzas, sin marcar
  const hoy = new Date()
  let puntuales = 0, tardanzas = 0, sinMarcar = 0

  for (let i = 6; i >= 0; i--) {
    const d = new Date(hoy)
    d.setDate(hoy.getDate() - i)
    const fechaStr = d.toLocaleDateString('en-CA')

    try {
      const r = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: fechaStr, fecha_fin: fechaStr }
      })
      const statsDia = r.data.estadisticas || {}
      puntuales += statsDia.puntuales || 0
      tardanzas += statsDia.tardanzas || 0
      const total = statsDia.total_entradas || 0
      const punt = statsDia.puntuales || 0
      const tard = statsDia.tardanzas || 0
      sinMarcar += Math.max(0, total - (punt + tard))


    } catch (e) {
      console.error('Error stats semana:', e)
    }
  }

  // Si ya existe, destruir
  if (donaChart) donaChart.destroy()

  donaChart = new Chart(donaCanvas.value, {
    type: 'doughnut',
    data: {
      labels: ['Puntuales', 'Tardanzas', 'Sin marcar'],
      datasets: [{
        data: [puntuales, tardanzas, sinMarcar],
        backgroundColor: ['#10b981', '#f58300', '#dfdfe4'],
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#64748b' } },
        tooltip: { callbacks: {
          label: function(context) {
            return `${context.label}: ${context.raw}`
          }
        }}
      }
    }
  })
}


// Gráfico de lineas 
async function construirLineas() {
  if (!lineCanvas.value) return

  const hoy = new Date()
  const labels = []
  const entradas = []
  const tardanzas = []

  for (let i = 6; i >= 0; i--) {
    const d = new Date(hoy)
    d.setDate(hoy.getDate() - i)
    const fechaStr = d.toLocaleDateString('en-CA')
    labels.push(DIAS[d.getDay()].substring(0, 3))

    try {
      const r = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: fechaStr, fecha_fin: fechaStr }
      })
      const puntuales = r.data.estadisticas?.puntuales || 0
      const tard = r.data.estadisticas?.tardanzas || 0

      entradas.push(puntuales)
      tardanzas.push(tard)
    } catch (e) {
      entradas.push(0)
      tardanzas.push(0)
    }
  }

  if (lineChart) lineChart.destroy()

  lineChart = new Chart(lineCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Puntuales',
          data: entradas,
          borderColor: '#10b981',
          backgroundColor: 'rgba(26,58,107,0.08)',
          borderWidth: 2.5,
          pointBackgroundColor: '#10b981',
          pointRadius: 4,
          tension: 0.4,
          fill: true,
        },
        {
          label: 'Tardanzas',
          data: tardanzas,
          borderColor: '#f58300',
          backgroundColor: 'rgba(245,158,11,0.08)',
          borderWidth: 2.5,
          pointBackgroundColor: '#f58300',
          pointRadius: 4,
          tension: 0.4,
          fill: true,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { mode: 'index', intersect: false }
      },
      scales: {
        x: { ticks: { color: '#94a3b8 ', font: { size: 11 } }, grid: { display: false } },
        y: {
          beginAtZero: true,
          ticks: { color: '#94a3b8 ', font: { size: 11 }, stepSize: 1 },
          grid: { color: 'rgba(0,0,0,0.04)' }
        }
      }
    }
  })
}

// Marcaciones con geolocalización 
const marcacionesConGeo = computed(() =>
  marcacionesHoy.value.filter(m => m.latitud && m.longitud).length
)

// Puntos del mapa
// Agrupa marcaciones por ciudad y las ubica en posiciones relativas dentro del SVG (300x200)

function iniciarMapa() {
  const contenedor = document.getElementById('mapa-leaflet')
  if (!contenedor) return

  if (!window.L) {
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    document.head.appendChild(link)

    const script = document.createElement('script')
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.onload = () => renderizarMapa(contenedor)
    document.head.appendChild(script)
  } else {
    renderizarMapa(contenedor)
  }
}

function renderizarMapa(contenedor) {
  const L = window.L

  if (contenedor._leaflet_id) {
    contenedor._leaflet_id = null
    contenedor.innerHTML = ''
  }

  const mapa = L.map(contenedor).setView([-7.1518, -78.5117], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapa)

  const conGeo = marcacionesHoy.value.filter(m => m.latitud && m.longitud)

  if (conGeo.length === 0) {
    // Mostrar TODAS las marcaciones con GPS
    marcacionesHoy.value.forEach((m, i) => {
      const lat = -7.1626 + (Math.random() * 0.01)
      const lng = -78.5001 + (Math.random() * 0.01)
      
      const marker = L.marker([lat, lng]).addTo(mapa)
      marker.bindPopup(`
      <b>${m.trabajador_nombre}</b><br>
      ${m.tipo} — ${m.estado || ''}<br>
      ${formatHora(m.fecha)}
      
      `)

      // HOVER 
      marker.bindTooltip(
        `${m.trabajador_nombre}`,
        { direction: 'top', offset: [0, -10] }
      )
    })
    return
  }

  conGeo.forEach(m => {
    const lat = parseFloat(m.latitud)
    const lng = parseFloat(m.longitud)

    L.marker([lat, lng])
      .addTo(mapa)
      .bindPopup(`
        <b>${m.trabajador_nombre}</b><br>
        ${m.tipo} — ${m.estado || ''}<br>
        ${formatHora(m.fecha)}
      `)
  })
}


async function recargar() {
  cargando.value = true
  cargandoHoy.value = true
  await Promise.all([cargarEstadisticas(), cargarHoy()])
}


// Helpers 
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
  font-size: 1em;
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
  font-size: 0.93em;
  font-weight: 600;
  color: #1a3a6b;
  background: #f1f5f9;
  padding: 5px 12px;
}

.btn-refresh {
  background: #08c22a;
  color: rgb(255, 255, 255);
  font-size: 1.01em;
  font-weight: 600;
  border: none;
  padding: 11px 29px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #4a7ac2;
  color: #fff;
}

.btn-refresh:disabled {
  opacity: 0.6;
}

/* Para todas las métricas*/
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}
.mc {
  background: #fff;
  border-radius: 16px; 
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
  padding: 20px;
}

.mc:hover {
  transform: translateY(-8px);
  background: #000000;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
  padding: 20px;
}
.mc-label {
  font-size: 1.03em;
  font-weight: 500;
  color: #000000;
}

.mc-val {
  display: block;
  font-size: 1.7rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.mc-sub {
  font-size: 0.9em !important;
  display: flex;
  align-items: center;
  gap: 4px;
}

.mc:hover .mc-label,
.mc:hover .mc-val,
.mc:hover .mc-footer,
.mc-sub neutral .mc-sub up {
  color: #fff !important;
}

.mc-header {
  display: flex;
  align-items: center;
  gap: 12px; 
  margin-bottom: 12px;
}

.tarjeta-icono {
  width: 34px;
  height: 34px;
  padding: 8px;
  background: #dfdfe4; 
  border-radius: 8px;
  object-fit: contain;
}



/* para todas las cajas del dashboard*/
.card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8eaf0;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.card-title {
  font-size: 1.031em;
  font-weight: 600;
  color: #000;
}

.card-sub {
  font-size: 0.75rem;
  color: #9ca3af;
}

/* para el gráfico de linea */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 12px;
}

@media (max-width: 700px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-legend {
  display: flex;
  gap: 14px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.leg-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85em;
  color: #64748b;
}

.leg-dot {
  width: 12px;
  height: 12px;
  border-radius: 50px;
  flex-shrink: 0;
}

.chart-wrap {
  position: relative;
  height: 180px;
}

/* para el grafico circular*/
.dona-card .dona-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.dona-svg {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.dona-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dl-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.75rem;
  color: #64748b;
}

.dl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Fila inferior */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 700px) {
  .bottom-row {
    grid-template-columns: 1fr;
  }
}

/* Tabla de últimas marcaciones */
.act-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.act-table th {
  font-size: 1.05em;
  font-weight: 600;
  color: #0b50d0;
  padding: 6px 8px;
  border-bottom: 1px solid #f0f2f5;
  text-align: left;
}

.act-table td {
  padding: 8px 8px;
  border-bottom: 1px solid #f8fafc;
  color: #374151;
}

.act-table tr:last-child td {
  border-bottom: none;
}

.act-table tr:hover td {
  background: #f8fafc;
}

.td-nombre {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 1.02em;
}

.vacio {
  font-size: 1.1em;
  text-align: center;
  color: #9ca3af;
  padding: 20px !important;
}

/* ── Pills ── */
.pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
}

.pill-p {
  background: #16a363;
  color: #ffffff;
}

.pill-t {
  background: #f58300;
  color: #000000;
}

.pill-s {
  background: #0e1ce6;
  color: #ffffff;
}

/* ── Mapa ── */
.mapa-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mapa-leaflet {
  width: 100%;
  height: 220px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.mapa-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #64748b;
}

.ubi-marca p {
  font-size: 1.05em;
}


/* ── Cargando mini ── */
.mini-cargando { text-align: center; color: #9ca3af; font-size: 0.82rem; padding: 20px; }



</style>