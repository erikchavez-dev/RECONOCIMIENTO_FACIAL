<template>
  <div class="panel" :class="{ light: !theme.oscuro }" :style="bgStyle">
    <div class="bg-overlay"></div>

    <!-- HEADER -->
    <header class="header-bar">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-chip">
          <img :src="iconoPerfil" class="icono-perfil" />
          {{auth.usuario?.nombre_completo }}
        </span>
       <button @click="theme.toggle()" class="btn-sm" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">
          <img :src="theme.oscuro ? iconoSol : iconoLuna" alt="Icono Tema" class="icono-btn" />
        </button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="content">

    <!-- TOP: saludo centrado + frase -->
      <div class="top-section">
        <!-- Bloque Izquierdo -->
        <div class="frase-wrap" v-if="frase">
          <p class="frase-txt">"{{ frase }}"</p>
          <span class="frase-autor" v-if="fraseAutor">— {{ fraseAutor }}</span>
        </div>

        <!-- Bloque Derecho -->
        <div class="textos-usuario">
          <p class="saludo-txt">{{ saludo }}</p>
          <h1 class="nombre-grande">{{ auth.usuario?.nombre_completo }}</h1>
          <p class="fecha-sub">{{ fechaHoy }}</p>
        </div>
      </div>

      <!-- MAIN: botones izq + slider der -->
      <div class="main-layout">

        <!-- Botones verticales izquierda (35%) -->
        <div class="left-col">
          
          <div class="accion-btn principal" @click="$router.push('/trabajador/marcar')">
            <div class="accion-icon azul">
              <img :src="imagenReconocimiento" class="accion-img" />
            </div>
            <div class="ab-info">
              <h4>Marcar Asistencia</h4>
              <p>Registrar entrada o salida</p>
            </div>
            <span class="arrow">→</span>
          </div>

          <div class="accion-btn" @click="$router.push('/trabajador/asistencia')">
            <div class="accion-icon verde">
              <img :src="imagenAsistencia" class="accion-img" />
            </div>
            <div class="ab-info">
              <h4>Mi Asistencia</h4>
              <p>Ver resumen del mes</p>
            </div>
            <span class="arrow">→</span>
          </div>

          <div class="accion-btn" @click="$router.push('/trabajador/historial')">
            <div class="accion-icon naranja">
              <img :src="imagenHistorial" class="accion-img" />
            </div>
            <div class="ab-info">
              <h4>Mi Historial</h4>
              <p>Ver mis marcaciones</p>
            </div>
            <span class="arrow">→</span>
          </div>
        </div>

        <!-- Slider derecha (65%) -->
        <div class="right-col">
          <div class="slider-outer">

            <!-- Tabs -->
            <div class="slider-tabs">
              <button
                v-for="(tab, i) in tabs"
                :key="i"
                class="stab"
                :class="{ active: slideActivo === i }"
                @click="slideActivo = i"
              >
                {{ tab }}
              </button>
            </div>

            <!-- SLIDE 0: CLIMA -->
            <transition name="slide-fade">
              <div class="slide-content" v-show="slideActivo === 0">
                <div v-if="!clima" class="slide-loading">Cargando clima...</div>
                <template v-else>
                  <div class="clima-row">
                    <span class="clima-icon">{{ clima.icono }}</span>
                    <div class="clima-main">
                      <span class="clima-temp">{{ clima.temperatura }}°C</span>
                      <span class="clima-desc">{{ clima.descripcion }}</span>
                      <span class="clima-lugar">Ubicación actual</span>
                    </div>
                  </div>
                  <div class="clima-extra-row">
                    <div class="ce-item">
                      <div class="ce-label">Humedad</div>
                      <span class="ce-val">{{ clima.humedad }}%</span>
                    </div>
                    <div class="ce-item">
                      <div class="ce-label">Viento</div>
                      <span class="ce-val">{{ clima.viento }} km/h</span>
                    </div>
                    <div class="ce-item">
                      <div class="ce-label">Sensación</div>
                      <span class="ce-val">{{ clima.sensacion }}°C</span>
                    </div>
                    <div class="ce-item">
                      <div class="ce-label">Precip.</div>
                      <span class="ce-val">{{ clima.lluvia }} mm</span>
                    </div>
                  </div>
                </template>
              </div>
            </transition>

            <!-- SLIDE 1: CALENDARIO + FERIADOS -->
            <transition name="slide-fade">
              <div class="slide-content" v-show="slideActivo === 1">
                <div class="cal-head">
                  <button @click="mesAnterior" class="cal-nav-btn">‹</button>
                  <span class="cal-mes-txt">{{ nombreMes }} {{ anioCalendario }}</span>
                  <button @click="mesSiguiente" class="cal-nav-btn">›</button>
                </div>
                <div class="cal-semana">
                  <span v-for="d in ['Lu','Ma','Mi','Ju','Vi','Sá','Do']" :key="d">{{ d }}</span>
                </div>
                <div class="cal-grid">
                  <div
                    v-for="(dia, i) in diasCalendario"
                    :key="i"
                    :class="['cdia',
                      dia.vacio    ? 'vacio'    : '',
                      dia.esHoy    ? 'hoy'      : '',
                      dia.feriado  ? 'feriado'  : '',
                      dia.domingo  ? 'dom'      : '',
                    ]"
                    :title="dia.feriado ? dia.nombreFeriado : ''"
                  >{{ dia.vacio ? '' : dia.num }}</div>
                </div>
                <div class="cal-leyenda">
                  <span class="cl-item"><span class="cl-dot blanco"></span>Hoy</span>
                  <span class="cl-item"><span class="cl-dot amarillo"></span>Feriado nacional</span>
                </div>
              </div>
            </transition>

            <!-- SLIDE 2: ESTADO HOY -->
            <transition name="slide-fade">
              <div class="slide-content" v-show="slideActivo === 2">
                <div v-if="cargandoEstado" class="slide-loading">Cargando estado...</div>
                <template v-else>
                  <div class="estado-rows">
                    <div class="est-fila" :class="estadoEntrada.clase">
                      <img :src="estadoEntrada.icono" class="est-img-icon" alt="Estado" />
                      <div>
                        <div class="est-label">Entrada</div>
                        <div class="est-valor">{{ estadoEntrada.texto }}</div>
                      </div>
                    </div>
                    <div class="est-fila" :class="estadoSalida.clase">
                      <img :src="estadoSalida.icono" class="est-img-icon" alt="Estado" />
                      <div>
                        <div class="est-label">Salida</div>
                        <div class="est-valor">{{ estadoSalida.texto }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="tiempo-bloque" v-if="tiempoTrabajado">
                    <div class="tiempo-lbl">Tiempo trabajado hoy</div>
                    <span class="tiempo-num">{{ tiempoTrabajado }}</span>
                  </div>
                  <div class="tiempo-bloque sin-tiempo" v-else>
                    <div class="tiempo-lbl">Sin registro completo aún</div>
                  </div>
                </template>
              </div>
            </transition>

           <div class="slider-arrows">
              <button @click="slideActivo = (slideActivo - 1 + tabs.length) % tabs.length">‹</button>
              <button @click="slideActivo = (slideActivo + 1) % tabs.length">›</button>
            </div>
           <div class="slider-dots">
              <span v-for="(t, i) in tabs" :key="i" :class="{ active: slideActivo === i }"
                @click="slideActivo = i"></span>
            </div>

          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import imagenReconocimiento from '@/assets/icon-reconocimiento-facial.svg'
import imagenHistorial from '@/assets/lista-historial.webp'
import imagenAsistencia from '@/assets/asistencia.webp'
import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna from '@/assets/icon-luna.svg'
import iconoSol from '@/assets/icon-sol.svg'
import relojArena from '@/assets/reloj-de-arena.webp'
import iconoAlerta from '@/assets/alerta.webp'
import iconoCheck from '@/assets/icon-check.svg'

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const router = useRouter()
const auth   = useAuthStore()
const theme  = useThemeStore()

// ── Saludo ───────────────────────────────────────────────────
const saludo = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Buen día'
  if (h < 18) return 'Buena tarde'
  return 'Buena noche'
})
const fechaHoy = computed(() =>
  new Date().toLocaleDateString('es-PE', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
)

// ── FRASES ───────────────────────────────────────────────────
const FRASES = [
  { t: 'La disciplina es el puente entre metas y logros.', a: 'Jim Rohn' },
  { t: 'El éxito es repetir pequeños esfuerzos.', a: 'Robert Collier' },
  { t: 'Haz de cada día tu obra maestra.', a: 'John Wooden' },
  { t: 'La puntualidad es clave del éxito.', a: 'Autor' },
  { t: 'El trabajo duro vence al talento.', a: 'Tim Notke' },
  { t: 'No cuentes los días, haz que cuenten.', a: 'Muhammad Ali' },
  { t: 'El éxito es la suma de pequeños esfuerzos.', a: 'R. Collier' },
  { t: 'El futuro pertenece a los que se preparan hoy.', a: 'Malcolm X' },
]
const frase = ref('')
const fraseAutor = ref('')
function cargarFrase() {
  const f = FRASES[Math.floor(Math.random() * FRASES.length)]
  frase.value = f.t
  fraseAutor.value = f.a
}

// ── CLIMA ────────────────────────────────────────────────────
const clima = ref(null)
const WMO = {
  0:{d:'Despejado',i:'☀️'}, 1:{d:'Mayormente despejado',i:'🌤️'},
  2:{d:'Parcialmente nublado',i:'⛅'}, 3:{d:'Nublado',i:'☁️'},
  45:{d:'Neblina',i:'🌫️'}, 51:{d:'Llovizna',i:'🌦️'},
  61:{d:'Lluvia ligera',i:'🌧️'}, 63:{d:'Lluvia moderada',i:'🌧️'},
  80:{d:'Chubascos',i:'🌦️'}, 95:{d:'Tormenta',i:'⛈️'}
}

async function cargarClima() {
  try {
    const CACHE_KEY  = 'weather_cache'
    const CACHE_TIME = 10 * 60 * 1000
    const cacheRaw   = localStorage.getItem(CACHE_KEY)

    if (cacheRaw) {
      const cache = JSON.parse(cacheRaw)
      if (Date.now() - cache.timestamp < CACHE_TIME) {
        const c = cache.data.current
        const w = WMO[c.weathercode] || { d: 'Variable', i: '🌡️' }
        clima.value = {
          temperatura: Math.round(c.temperature_2m), humedad: c.relative_humidity_2m,
          viento: Math.round(c.windspeed_10m), sensacion: Math.round(c.apparent_temperature),
          lluvia: c.precipitation ?? 0, descripcion: w.d, icono: w.i,
        }
        return
      }
    }

    function getLocation() {
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
      })
    }
    let lat, lon
    try {
      const position = await getLocation()
      lat = position.coords.latitude
      lon = position.coords.longitude
    } catch {
      return await cargarClimaFallback()
    }

    const url  = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,apparent_temperature,precipitation&timezone=auto`
    const res  = await fetch(url)
    const data = await res.json()
    localStorage.setItem(CACHE_KEY, JSON.stringify({ data, timestamp: Date.now() }))
    const c = data.current
    const w = WMO[c.weathercode] || { d: 'Variable', i: '🌡️' }
    clima.value = {
      temperatura: Math.round(c.temperature_2m), humedad: c.relative_humidity_2m,
      viento: Math.round(c.windspeed_10m), sensacion: Math.round(c.apparent_temperature),
      lluvia: c.precipitation ?? 0, descripcion: w.d, icono: w.i,
    }
  } catch {
    await cargarClimaFallback()
  }
}

async function cargarClimaFallback() {
  try {
    const url  = 'https://api.open-meteo.com/v1/forecast?latitude=-7.1518&longitude=-78.5117&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,apparent_temperature,precipitation&timezone=America%2FLima'
    const res  = await fetch(url)
    const data = await res.json()
    const c    = data.current
    const w    = WMO[c.weathercode] || { d: 'Variable', i: '🌡️' }
    clima.value = {
      temperatura: Math.round(c.temperature_2m), humedad: c.relative_humidity_2m,
      viento: Math.round(c.windspeed_10m), sensacion: Math.round(c.apparent_temperature),
      lluvia: c.precipitation ?? 0, descripcion: w.d, icono: w.i,
    }
  } catch {
    clima.value = { temperatura: '--', humedad: '--', viento: '--', sensacion: '--', lluvia: 0, descripcion: 'Sin datos', icono: '🌡️' }
  }
}

// ── CALENDARIO ───────────────────────────────────────────────
const mesCalendario  = ref(new Date().getMonth())
const anioCalendario = ref(new Date().getFullYear())
const MESES_ES       = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes      = computed(() => MESES_ES[mesCalendario.value])

const feriadosCache = {}
const feriadosSet   = ref(new Set())

async function cargarFeriados(anio) {
  if (feriadosCache[anio]) { feriadosSet.value = feriadosCache[anio]; return }
  try {
    const res  = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${anio}/PE`)
    const data = await res.json()
    const set  = new Set()
    const names = {}
    data.forEach(f => { set.add(f.date); names[f.date] = f.localName })
    feriadosCache[anio] = { set, names }
    feriadosSet.value   = { set, names }
  } catch {
    feriadosSet.value = { set: new Set(), names: {} }
  }
}

const diasCalendario = computed(() => {
  const primer = new Date(anioCalendario.value, mesCalendario.value, 1)
  const ultimo = new Date(anioCalendario.value, mesCalendario.value + 1, 0)
  const inicio = (primer.getDay() + 6) % 7
  const hoy    = new Date()
  const hoyStr = `${hoy.getFullYear()}-${String(hoy.getMonth()+1).padStart(2,'0')}-${String(hoy.getDate()).padStart(2,'0')}`
  const dias   = []
  for (let i = 0; i < inicio; i++) dias.push({ vacio: true })
  for (let d = 1; d <= ultimo.getDate(); d++) {
    const mm        = String(mesCalendario.value + 1).padStart(2, '0')
    const dd        = String(d).padStart(2, '0')
    const fs        = `${anioCalendario.value}-${mm}-${dd}`
    const diaSemana = new Date(anioCalendario.value, mesCalendario.value, d).getDay()
    const esFeriado = feriadosSet.value?.set?.has(fs)
    dias.push({
      num: d, vacio: false, esHoy: fs === hoyStr,
      feriado: esFeriado,
      nombreFeriado: esFeriado ? (feriadosSet.value?.names?.[fs] || 'Feriado') : '',
      domingo: diaSemana === 0,
    })
  }
  return dias
})

function mesAnterior() {
  if (mesCalendario.value === 0) { mesCalendario.value = 11; anioCalendario.value-- }
  else mesCalendario.value--
  cargarFeriados(anioCalendario.value)
}
function mesSiguiente() {
  if (mesCalendario.value === 11) { mesCalendario.value = 0; anioCalendario.value++ }
  else mesCalendario.value++
  cargarFeriados(anioCalendario.value)
}

// ── ESTADO HOY ───────────────────────────────────────────────
// Usa el historial directo en lugar de asistencia,
// así funciona independientemente de va_a_asistencia y migraciones.
const cargandoEstado = ref(true)
const estadoEntrada  = ref({ icono: relojArena, texto: 'Sin registro', clase: 'pendiente' })
const estadoSalida   = ref({ icono: relojArena, texto: 'Sin registro', clase: 'pendiente' })
const tiempoTrabajado = ref(null)

// Tipos que representan una entrada o salida válida para mostrar en el panel
const TIPOS_ENTRADA = ['ENTRADA_VALIDA', 'ENTRADA']
const TIPOS_SALIDA  = ['SALIDA_VALIDA',  'SALIDA']

async function cargarEstadoHoy() {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const res = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    const todas = res.data || []

    // Filtrar solo las del día de hoy (comparando fecha local)
    const hoyStr = new Date().toLocaleDateString('en-CA') // YYYY-MM-DD en local

    const hoy = todas.filter(m => {
      const fechaLocal = new Date(m.fecha).toLocaleDateString('en-CA')
      return fechaLocal === hoyStr
    })

    // Buscar la primera entrada válida del día (que afecte asistencia)
    // Si no hay con va_a_asistencia, tomar cualquier ENTRADA/ENTRADA_VALIDA del día
    let entrada = hoy.find(m => TIPOS_ENTRADA.includes(m.tipo) && m.va_a_asistencia === true)
    if (!entrada) {
      // Fallback: cualquier entrada del día (compatible con registros viejos)
      entrada = hoy.find(m => TIPOS_ENTRADA.includes(m.tipo) && m.exitoso !== false)
    }

    let salida = hoy.find(m => TIPOS_SALIDA.includes(m.tipo) && m.va_a_asistencia === true)
    if (!salida) {
      salida = hoy.find(m => TIPOS_SALIDA.includes(m.tipo) && m.exitoso !== false)
    }

    if (entrada) {
      const horaEntrada = new Date(entrada.fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })
      const esPuntual = entrada.estado === 'PUNTUAL'
      estadoEntrada.value = {
        icono: esPuntual ? iconoCheck : iconoAlerta,
        texto: `${horaEntrada} — ${esPuntual ? 'Puntual' : entrada.estado === 'TARDANZA' ? 'Tardanza' : 'Registrada'}`,
        clase: esPuntual ? 'ok' : 'tarde',
      }
    }

    if (salida) {
      const horaSalida = new Date(salida.fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })
      estadoSalida.value = { icono: iconoCheck, texto: horaSalida, clase: 'ok' }
    }

    // Calcular tiempo trabajado si hay entrada y salida
    if (entrada && salida) {
      const entradaDt = new Date(entrada.fecha)
      const salidaDt  = new Date(salida.fecha)
      const diffSeg   = Math.floor((salidaDt - entradaDt) / 1000)
      if (diffSeg > 0) {
        const hh = Math.floor(diffSeg / 3600)
        const mm = Math.floor((diffSeg % 3600) / 60)
        const ss = diffSeg % 60
        tiempoTrabajado.value = `${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}:${String(ss).padStart(2,'0')}`
      }
    }

  } catch (e) {
    console.error('Error estado hoy:', e)
  } finally {
    cargandoEstado.value = false
  }
}

// ── Slider ───────────────────────────────────────────────────
const tabs        = ['Clima', 'Calendario', 'Estado hoy']
const slideActivo = ref(0)
let sliderInterval = null
function iniciarSliderAuto() {
  sliderInterval = setInterval(() => {
    slideActivo.value = (slideActivo.value + 1) % tabs.length
  }, 20000)
}

// ── Init ─────────────────────────────────────────────────────
onMounted(async () => {
  cargarFrase()
  cargarClima()
  cargarFeriados(anioCalendario.value)
  cargarEstadoHoy()
  iniciarSliderAuto()
})

onUnmounted(() => {
  if (sliderInterval) clearInterval(sliderInterval)
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── BASE ── */
.panel {
  --bg-main: #141416cc;
  --bg-card: #141416;
  --bg-soft: rgba(255,255,255,0.08);
  --text-main: #fcfcfd;
  --text-soft: rgba(255,255,255,0.6);
  --border-color: #232327;
  --accent: #18c440;
}
.panel.light {
  --bg-main: #f8fafc;
  --bg-card: #ffffff;
  --bg-soft: #f1f5f9;
  --text-main: #0f172a;
  --text-soft: #64748b;
  --border-color: #e2e8f0;
  --accent: #2563eb;
}

.panel {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background-color: var(--bg-main);
  color: var(--text-main);
}

.bg-overlay {
  background: radial-gradient(circle at top right, #0000000d, transparent);
}

/* TEMA CLARO overrides */
.panel.light .accion-btn:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  transform: translateX(5px);
}
.panel.light .slider-arrows button { background: #e2e8f0; color: #1e293b; }
.panel.light .slider-arrows button:hover { background: var(--accent); color: white; }
.panel.light .content { background: var(--bg-main); }
.panel.light .header-bar { background: white; border-bottom: 1px solid var(--border-color); }
.panel.light .accion-btn,
.panel.light .slider-outer,
.panel.light .frase-wrap { box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid var(--border-color); }
.panel.light .accion-btn.principal { background: #22c55e; color: white; }
.panel.light .accion-btn.principal:hover { background: #16a34a; }
.panel.light .accion-btn { background: white; color: var(--text-main); }
.panel.light .accion-btn:hover { border-color: var(--accent); transform: translateX(5px); }
.panel.light .slider-outer { background: white; }
.panel.light .stab { color: var(--text-soft); }
.panel.light .stab.active { color: var(--accent); border-bottom: 2px solid var(--accent); }
.panel.light .nombre-grande { color: var(--text-main); }
.panel.light .saludo-txt, .panel.light .fecha-sub { color: var(--text-main); }
.panel.light .frase-wrap { background: #c7c9ca; border-left: 4px solid var(--accent); }
.panel.light .frase-txt { color: var(--text-main); }
.panel.light .frase-autor { color: var(--text-soft); }
.panel.light .ce-item { background: #f8fafc; border: 1px solid var(--border-color); }
.panel.light .accion-img { filter: none; }
.panel.light .slide-content,
.panel.light .slider-tabs,
.panel.light .ce-item { background: var(--text-main); }
.panel.light .est-fila { background: #192775; }

/* ── HEADER ── */
.header-bar {
  position: relative; z-index: 10;
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 28px; border-bottom: 2px solid var(--accent); background: var(--bg-card);
}
.header-left { display: flex; align-items: center; gap: 10px; }
.header-right { display: flex; align-items: center; gap: 10px; }
.logo { width: 150px; height: 50px; object-fit: contain; }
.sistema-nombre { color: var(--text-main); font-weight: 600; font-size: 0.95rem; opacity: 0.9; }
.nombre-chip {
  display: flex; align-items: center; gap: 6px; color: white;
  font-size: 0.82rem; background: rgba(255,255,255,0.1); padding: 9px 35px; border-radius: 6px;
}
.icono-perfil { width: 18px; height: 18px; }
.btn-sm {
  display: flex; align-items: center; justify-content: center;
  padding: 5px 25px; cursor: pointer; background: #232324; border: 1px solid #ddd; border-radius: 4px;
}
.btn-sm:hover { background: #ffffff; }
.icono-btn { width: 18px; height: 18px; display: block; }
.btn-logout {
  background: red; border: 1px solid rgba(255,255,255,0.35);
  color: #ffffff; padding: 9px 42px; border-radius: 6px; cursor: pointer; font-size: 0.82rem;
}
.btn-logout:hover { background: #000000; color: #ff0000; }

/* ── CONTENT ── */
.content {
  position: relative; z-index: 10; flex: 1;
  padding: 28px 32px 24px; display: flex; flex-direction: column; gap: 24px;
  background-color: #141416cc;
}

/* ── TOP ── */
.top-section {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 20px;
}
.textos-usuario { flex: 1; text-align: center; }
.saludo-txt { font-size: 1em; letter-spacing: 1px; text-transform: uppercase; color: var(--text-soft); margin-bottom: 4px; }
.nombre-grande { font-size: 2.3rem; font-weight: 700; color: white; line-height: 1; margin-bottom: 4px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.fecha-sub { font-size: 0.93em; color: var(--text-soft); text-transform: capitalize; margin-bottom: 12px; }
.frase-wrap {
  flex: 0 1 410px; background: var(--bg-soft); border-radius: 10px;
  padding: 10px 18px; border-left: 3px solid var(--accent); text-align: left; margin: 0;
}
.frase-txt {
  font-size: 1.08em; color: rgba(255,255,255,0.85); font-style: italic; line-height: 1;
  margin: 0; display: block; overflow: hidden; display: -webkit-box;
  -webkit-box-orient: vertical; -webkit-line-clamp: 5; line-clamp: 5;
}
.frase-autor { font-size: 0.92em; color: rgba(255,255,255,0.5); display: block; margin-top: 4px; }

/* ── MAIN LAYOUT ── */
.main-layout { display: flex; gap: 60px; flex: 1; align-items: stretch; justify-content: space-between; }

/* ── BOTONES IZQUIERDA ── */
.left-col { width: 32%; display: flex; flex-direction: column; gap: 12px; justify-content: center; }
.accion-btn {
  display: flex; align-items: center; gap: 14px; padding: 16px 18px; border-radius: 14px;
  background: var(--bg-card); color: white; border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0,0,0,0.5); cursor: pointer; transition: all 0.2s ease; text-decoration: none;
}
.accion-btn:hover { background: #1c1c1f; border-color: #18c440; box-shadow: 0 0 15px rgba(24,196,64,0.2); transform: translateX(5px); }
.accion-btn.principal { background: #18c440; border-color: transparent; color: #0a0a0b; }
.accion-btn.principal:hover { background: white; transform: translateX(5px) scale(1.01); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.accion-btn.principal .ab-info h4, .accion-btn.principal .ab-info p, .accion-btn.principal .arrow { color: #0a0a0b; }
.accion-icon { width: 44px; height: 44px; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0; }
.accion-icon.azul { background: #041a61; color: white; }
.accion-icon.verde { background: rgba(34,197,94,0.2); }
.accion-icon.naranja { background: rgba(251,146,60,0.2); }
.accion-btn.principal .accion-icon.azul { background: #041a61; }
.accion-img { width: 30px; height: 30px; object-fit: contain; border-radius: 6px; filter: brightness(0) invert(1); }
.ab-info { flex: 1; }
.ab-info h4 { font-size: 1.15em; font-weight: 600; margin: 0 0 2px; }
.ab-info p { font-size: 0.92em; font-weight: 500; opacity: 0.7; margin: 0; }
.accion-btn.principal .ab-info h4 { color: #041a61; }
.accion-btn.principal .ab-info p { color: #041a61; opacity: 0.65; }
.arrow { font-size: 1rem; opacity: 0.4; flex-shrink: 0; margin-left: auto; }
.accion-btn.principal .arrow { opacity: 0.4; color: #1a3a6b; }

/* ── SLIDER ── */
.right-col { flex: 1; min-height: 320px; }
.slider-outer {
  height: 370px; border-radius: 16px; overflow: hidden;
  border: 1px solid var(--border-color); background: var(--bg-card);
  backdrop-filter: blur(10px); display: flex; flex-direction: column; position: relative;
}
.slider-tabs { display: flex; border-bottom: 1px solid rgba(255,255,255,0.1); flex-shrink: 0; }
.stab {
  flex: 1; padding: 11px; text-align: center; font-size: 0.78rem;
  color: rgba(255,255,255,0.5); cursor: pointer; border: none; background: none; transition: all 0.2s;
}
.stab:hover { color: white; background: rgba(255,255,255,0.07); }
.stab.active { color: #18c440; font-weight: 600; background: rgba(255,255,255,0.12); border-bottom: 2px solid #18c440; }
.slide-content { flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto; height: 100%; }
.slider-arrows { position: absolute; bottom: 20px; right: 20px; display: flex; gap: 10px; z-index: 10; }
.slider-arrows button {
  background: rgba(0,0,0,0.5); color: white; border: none; padding: 15px;
  border-radius: 50%; cursor: pointer; display: flex; height: 45px; width: 45px;
  align-items: center; justify-content: center; transition: background 0.3s ease;
}
.slider-arrows button:hover { background: #00ff84; color: #000; }
.slide-loading { color: rgba(255,255,255,0.5); font-size: 0.85rem; text-align: center; margin: auto; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: opacity 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; }

/* ── CLIMA ── */
.clima-row { display: flex; align-items: center; gap: 16px; }
.clima-icon { font-size: 3rem; line-height: 1; }
.clima-main { display: flex; flex-direction: column; gap: 2px; }
.clima-temp { font-size: 2.2rem; font-weight: 700; color: white; line-height: 1; }
.clima-desc { font-size: 0.82rem; color: rgba(255,255,255,0.65); }
.clima-lugar { font-size: 0.72rem; color: rgba(255,255,255,0.4); }
.clima-extra-row { display: flex; gap: 10px; flex-wrap: wrap; }
.ce-item { flex: 1; min-width: 70px; background: var(--bg-soft); border-radius: 10px; padding: 10px 12px; }
.ce-label { font-size: 0.68rem; color: rgba(255,255,255,0.5); display: block; margin-bottom: 4px; }
.ce-val { font-size: 1rem; font-weight: 600; color: white; display: block; }

/* ── CALENDARIO ── */
.cal-head { display: flex; justify-content: space-between; align-items: center; }
.cal-mes-txt { font-size: 0.88rem; font-weight: 700; color: white; }
.cal-nav-btn { background: rgba(255,255,255,0.1); border: none; color: white; width: 26px; height: 26px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
.cal-nav-btn:hover { background: rgba(255,255,255,0.2); }
.cal-semana { display: grid; grid-template-columns: repeat(7, 1fr); }
.cal-semana span { text-align: center; font-size: 0.65rem; color: rgba(255,255,255,0.4); font-weight: 600; padding: 4px 0; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }
.cdia { height: 28px; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; border-radius: 6px; color: rgba(255,255,255,0.7); }
.cdia.hoy { position: relative; z-index: 1; font-weight: 800; color: white; }
.cdia.hoy::after { content: ''; position: absolute; inset: 2px; background: rgba(156,163,175,0.25); border-radius: 6px; z-index: 0; }
.cdia.feriado { background: rgba(251,191,36,0.25); color: #fcd34d; font-weight: 700; }
.cdia.dom { color: rgba(252,165,165,0.75); }
.cdia.vacio { pointer-events: none; }
.cal-leyenda { display: flex; gap: 14px; margin-top: 6px; }
.cl-item { display: flex; align-items: center; gap: 5px; font-size: 0.68rem; color: rgba(255,255,255,0.45); }
.cl-dot { width: 8px; height: 8px; border-radius: 3px; }
.cl-dot.blanco { background: white; }
.cl-dot.amarillo { background: #fcd34d; }

/* ── ESTADO HOY ── */
.estado-rows { display: flex; flex-direction: column; gap: 10px; }
.est-fila { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 10px; background: var(--bg-soft); }
.est-fila.ok { background: rgba(24,196,64,0.1); border-left: 4px solid #18c440; }
.est-fila.tarde { background: rgba(251,191,36,0.15); }
.est-icon { font-size: 1.3rem; flex-shrink: 0; }
.est-label { font-size: 1.03em; color: rgba(255,255,255,0.45); text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 2px; }
.est-valor { font-size: 0.9em; font-weight: 600; color: white; }
.tiempo-bloque { background: rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; text-align: center; }
.tiempo-lbl { font-size: 1em; color: rgba(255,255,255,0.45); display: block; margin-bottom: 4px; }
.tiempo-num { font-family: monospace; font-size: 1.8rem; font-weight: 800; color: white; display: block; }
.sin-tiempo { opacity: 0.6; }
.est-img-icon { width: 28px; height: 28px; object-fit: contain; }
.est-fila.tarde .est-img-icon { filter: drop-shadow(0 0 4px rgba(255,68,68,0.4)); }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .header-bar { flex-direction: column; align-items: flex-start; gap: 10px; padding: 12px 16px; }
  .header-right { width: 100%; justify-content: space-between; }
  .logo { width: 110px; height: auto; }
  .sistema-nombre { font-size: 0.8rem; }
  .nombre-chip { padding: 6px 10px; font-size: 0.75rem; }
  .btn-logout { padding: 6px 12px; font-size: 0.75rem; }
  .content { padding: 16px; gap: 16px; }
  .top-section { flex-direction: column; align-items: stretch; gap: 12px; }
  .frase-wrap { width: 100%; font-size: 0.9rem; max-height: 70px; }
  .textos-usuario { text-align: center; }
  .nombre-grande { font-size: 1.6rem; }
  .saludo-txt { font-size: 0.8rem; }
  .fecha-sub { font-size: 0.8rem; }
  .main-layout { flex-direction: column; gap: 18px; }
  .left-col { width: 100%; gap: 10px; }
  .accion-btn { padding: 14px; border-radius: 12px; }
  .accion-btn:hover { transform: none; }
  .ab-info h4 { font-size: 1rem; }
  .ab-info p { font-size: 0.8rem; }
  .right-col { width: 100%; }
  .slider-outer { height: auto; min-height: 300px; }
  .slide-content { padding: 14px; }
  .stab { font-size: 0.7rem; padding: 8px; }
  .clima-temp { font-size: 1.6rem; }
  .clima-icon { font-size: 2.2rem; }
  .ce-item { flex: 1 1 45%; }
  .cdia { height: 24px; font-size: 0.65rem; }
  .cal-mes-txt { font-size: 0.8rem; }
  .est-fila { padding: 10px; }
  .est-label { font-size: 0.8rem; }
  .est-valor { font-size: 0.8rem; }
  .tiempo-num { font-size: 1.4rem; }
  .slider-arrows { bottom: 8px; right: 10px; }
  .slider-arrows button { width: 35px; height: 35px; padding: 10px; }
  .slider-dots { bottom: 10px; }
  .accion-btn { box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
  .slider-outer { border-radius: 20px; }
  .panel { padding-bottom: 20px; }
}
</style>