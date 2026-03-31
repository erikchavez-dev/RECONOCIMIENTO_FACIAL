<template>
  <div class="panel">

    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <div class="usuario-info">
          <img :src="iconoPerfil" class="icono-perfil" />
          <span class="nombre-usuario">{{ auth.usuario?.nombre_completo }}</span>
        </div>
        <button @click="theme.toggle()" class="btn-tema" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">
          {{ theme.oscuro ? '☀️' : '🌙' }}
        </button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="main">

      <!-- BIENVENIDA + CLIMA -->
      <div class="hero-section">
        <div class="bienvenida-bloque">
          <p class="saludo">{{ saludo }},</p>
          <h1 class="nombre-grande">{{ primerNombre }}</h1>
          <p class="fecha-hoy">{{ fechaHoy }}</p>
          <div class="frase-bloque" v-if="frase">
            <span class="comilla">"</span>
            <p class="frase-texto">{{ frase }}</p>
            <span class="frase-autor" v-if="fraseAutor">— {{ fraseAutor }}</span>
          </div>
        </div>
        <div class="clima-bloque" v-if="clima">
          <div class="clima-icono">{{ clima.icono }}</div>
          <div class="clima-datos">
            <span class="clima-temp">{{ clima.temperatura }}°C</span>
            <span class="clima-desc">{{ clima.descripcion }}</span>
            <span class="clima-lugar">Cajamarca, PE</span>
          </div>
          <div class="clima-extra">
            <div class="clima-extra-item">
              <span class="extra-label">💧 Humedad</span>
              <span class="extra-val">{{ clima.humedad }}%</span>
            </div>
            <div class="clima-extra-item">
              <span class="extra-label">💨 Viento</span>
              <span class="extra-val">{{ clima.viento }} km/h</span>
            </div>
          </div>
        </div>
        <div class="clima-bloque clima-loading" v-else>
          <div class="clima-spinner"></div>
        </div>
      </div>

      <!-- BOTONES DE ACCIÓN -->
      <div class="acciones-grid">
        <div class="accion-card accion-principal" @click="$router.push('/trabajador/marcar')">
          <div class="accion-icono-wrap azul">
            <img :src="imagenReconocimiento" class="accion-img" />
          </div>
          <div class="accion-info">
            <h3>Marcar Asistencia</h3>
            <p>Registrar entrada o salida</p>
          </div>
          <span class="accion-arrow">→</span>
        </div>
        <div class="accion-card" @click="$router.push('/trabajador/asistencia')">
          <div class="accion-icono-wrap verde">
            <span class="accion-emoji">📋</span>
          </div>
          <div class="accion-info">
            <h3>Mi Asistencia</h3>
            <p>Ver resumen del mes</p>
          </div>
          <span class="accion-arrow">→</span>
        </div>
        <div class="accion-card" @click="$router.push('/trabajador/historial')">
          <div class="accion-icono-wrap naranja">
            <img :src="imagenHistorial" class="accion-img" />
          </div>
          <div class="accion-info">
            <h3>Mi Historial</h3>
            <p>Ver mis marcaciones</p>
          </div>
          <span class="accion-arrow">→</span>
        </div>
      </div>

      <!-- INFERIOR: CALENDARIO + ESTADO HOY -->
      <div class="inferior-grid">

        <!-- CALENDARIO -->
        <div class="calendario-card">
          <div class="cal-header">
            <button @click="mesAnterior" class="cal-nav">‹</button>
            <span class="cal-titulo">{{ nombreMes }} {{ anioCalendario }}</span>
            <button @click="mesSiguiente" class="cal-nav">›</button>
          </div>
          <div class="cal-dias-semana">
            <span v-for="d in ['Lu','Ma','Mi','Ju','Vi','Sá','Do']" :key="d">{{ d }}</span>
          </div>
          <div class="cal-grid">
            <div
              v-for="(dia, i) in diasCalendario"
              :key="i"
              :class="['cal-dia', dia.vacio?'cal-vacio':'', dia.esHoy?'cal-hoy':'', dia.esFeriado?'cal-feriado':'', dia.esDomingo?'cal-domingo':'']"
              :title="dia.esFeriado ? dia.nombreFeriado : ''"
            >{{ dia.vacio ? '' : dia.num }}</div>
          </div>
          <div class="cal-leyenda">
            <span class="leg-item"><span class="leg-dot hoy"></span> Hoy</span>
            <span class="leg-item"><span class="leg-dot feriado"></span> Feriado</span>
          </div>
        </div>

        <!-- ESTADO HOY -->
        <div class="estado-card">
          <h3 class="estado-titulo">Estado de hoy</h3>
          <div v-if="cargandoEstado" class="estado-loading">Cargando...</div>
          <div v-else class="estado-contenido">
            <div class="estado-fila" :class="estadoEntrada.clase">
              <span class="estado-icono">{{ estadoEntrada.icono }}</span>
              <div class="estado-texto">
                <span class="estado-label">Entrada</span>
                <span class="estado-valor">{{ estadoEntrada.texto }}</span>
              </div>
            </div>
            <div class="estado-fila" :class="estadoSalida.clase">
              <span class="estado-icono">{{ estadoSalida.icono }}</span>
              <div class="estado-texto">
                <span class="estado-label">Salida</span>
                <span class="estado-valor">{{ estadoSalida.texto }}</span>
              </div>
            </div>
            <div v-if="tiempoTrabajadoHoy" class="tiempo-hoy">
              <span class="tiempo-label">⏱ Tiempo trabajado hoy</span>
              <span class="tiempo-valor">{{ tiempoTrabajadoHoy }}</span>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import imagenReconocimiento from '@/assets/reconocimiento.webp'
import imagenHistorial from '@/assets/historial.webp'
import iconoPerfil from '@/assets/icon-perfil.svg'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const router = useRouter()
const auth   = useAuthStore()
const theme  = useThemeStore()

const primerNombre = computed(() => auth.usuario?.nombre_completo?.split(' ')[0] || '')
const saludo = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 18) return 'Buenas tardes'
  return 'Buenas noches'
})
const fechaHoy = computed(() => new Date().toLocaleDateString('es-PE', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
}))

// CLIMA
const clima = ref(null)
const WMO = { 0:{d:'Despejado',i:'☀️'},1:{d:'Mayormente despejado',i:'🌤️'},2:{d:'Parcialmente nublado',i:'⛅'},3:{d:'Nublado',i:'☁️'},45:{d:'Neblina',i:'🌫️'},51:{d:'Llovizna',i:'🌦️'},61:{d:'Lluvia',i:'🌧️'},80:{d:'Chubascos',i:'🌦️'},95:{d:'Tormenta',i:'⛈️'} }
async function cargarClima() {
  try {
    const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-7.1518&longitude=-78.5117&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m&timezone=America%2FLima')
    const data = await res.json()
    const c = data.current
    const w = WMO[c.weathercode] || {d:'Variable',i:'🌡️'}
    clima.value = { temperatura: Math.round(c.temperature_2m), humedad: c.relative_humidity_2m, viento: Math.round(c.windspeed_10m), descripcion: w.d, icono: w.i }
  } catch { clima.value = { temperatura:'--', humedad:'--', viento:'--', descripcion:'Sin datos', icono:'🌡️' } }
}

// FRASE
const frase = ref('')
const fraseAutor = ref('')
const FRASES = [
  {t:'El éxito es la suma de pequeños esfuerzos repetidos día tras día.',a:'Robert Collier'},
  {t:'La disciplina es el puente entre las metas y los logros.',a:'Jim Rohn'},
  {t:'No cuentes los días, haz que los días cuenten.',a:'Muhammad Ali'},
  {t:'El trabajo duro supera al talento cuando el talento no trabaja duro.',a:'Tim Notke'},
  {t:'Cada día es una nueva oportunidad para cambiar tu vida.',a:''},
  {t:'La puntualidad es la cortesía de los reyes.',a:'Luis XVIII'},
  {t:'Haz de cada día tu obra maestra.',a:'John Wooden'},
  {t:'El único modo de hacer un gran trabajo es amar lo que haces.',a:'Steve Jobs'},
  {t:'Comienza donde estás. Usa lo que tienes. Haz lo que puedas.',a:'Arthur Ashe'},
  {t:'La constancia es la virtud por la que todas las otras virtudes dan sus frutos.',a:''},
  {t:'Un buen comienzo de día marca el ritmo de todo lo que sigue.',a:''},
  {t:'La excelencia no es un destino, sino un viaje continuo.',a:''},
]
function cargarFrase() {
  const ahora = new Date()
  const diff = ahora - new Date(ahora.getFullYear(), 0, 0)
  const dia = Math.floor(diff / 86400000)
  const f = FRASES[dia % FRASES.length]
  frase.value = f.t; fraseAutor.value = f.a
}

// ESTADO HOY
const cargandoEstado = ref(true)
const estadoEntrada = ref({ icono:'⏳', texto:'Sin registro', clase:'estado-pendiente' })
const estadoSalida  = ref({ icono:'⏳', texto:'Sin registro', clase:'estado-pendiente' })
const tiempoTrabajadoHoy = ref(null)
async function cargarEstadoHoy() {
  try {
    const hoyStr = new Date().toISOString().split('T')[0]
    const res = await api.get('/api/marcaciones/asistencia/', { params:{ fecha_inicio:hoyStr, fecha_fin:hoyStr } })
    const dias = res.data.dias
    if (dias.length > 0) {
      const hoy = dias[0]
      if (hoy.entrada_hora) estadoEntrada.value = { icono: hoy.entrada_estado==='PUNTUAL'?'✅':'⚠️', texto:`${hoy.entrada_hora} — ${hoy.entrada_estado}`, clase: hoy.entrada_estado==='PUNTUAL'?'estado-ok':'estado-tarde' }
      if (hoy.salida_hora)  estadoSalida.value  = { icono:'✅', texto:hoy.salida_hora, clase:'estado-ok' }
      tiempoTrabajadoHoy.value = hoy.tiempo_trabajado
    }
  } catch(e) { console.error(e) } finally { cargandoEstado.value = false }
}

// CALENDARIO
const MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const ahora = new Date()
const mesCalendario  = ref(ahora.getMonth())
const anioCalendario = ref(ahora.getFullYear())
const nombreMes = computed(() => MESES[mesCalendario.value])

const FERIADOS = ['2025-01-01','2025-04-17','2025-04-18','2025-05-01','2025-06-07','2025-06-29','2025-07-28','2025-07-29','2025-08-30','2025-10-08','2025-11-01','2025-12-08','2025-12-25','2026-01-01','2026-04-02','2026-04-03','2026-05-01','2026-06-07','2026-06-29','2026-07-28','2026-07-29','2026-08-30','2026-10-08','2026-11-01','2026-12-08','2026-12-25']
const NOMBRES_F = {'01-01':'Año Nuevo','05-01':'Día del Trabajo','06-07':'Batalla de Arica','06-29':'San Pedro y San Pablo','07-28':'Fiestas Patrias','07-29':'Fiestas Patrias','08-30':'Santa Rosa de Lima','10-08':'Combate de Angamos','11-01':'Todos los Santos','12-08':'Inmaculada Concepción','12-25':'Navidad'}

const diasCalendario = computed(() => {
  const primer = new Date(anioCalendario.value, mesCalendario.value, 1)
  const ultimo = new Date(anioCalendario.value, mesCalendario.value + 1, 0)
  const inicio = (primer.getDay() + 6) % 7
  const hoyStr = new Date().toISOString().split('T')[0]
  const dias = []
  for (let i = 0; i < inicio; i++) dias.push({ vacio:true })
  for (let d = 1; d <= ultimo.getDate(); d++) {
    const mm = String(mesCalendario.value+1).padStart(2,'0')
    const dd = String(d).padStart(2,'0')
    const fs = `${anioCalendario.value}-${mm}-${dd}`
    const mmdd = `${mm}-${dd}`
    const ef = FERIADOS.includes(fs)
    dias.push({ num:d, vacio:false, esHoy:fs===hoyStr, esFeriado:ef, esDomingo:new Date(anioCalendario.value,mesCalendario.value,d).getDay()===0, nombreFeriado:ef?(NOMBRES_F[mmdd]||'Feriado'):'' })
  }
  return dias
})
function mesAnterior() { if(mesCalendario.value===0){mesCalendario.value=11;anioCalendario.value--}else mesCalendario.value-- }
function mesSiguiente() { if(mesCalendario.value===11){mesCalendario.value=0;anioCalendario.value++}else mesCalendario.value++ }

onMounted(() => { cargarClima(); cargarFrase(); cargarEstadoHoy() })
async function handleLogout() { await auth.logout(); router.push('/login') }
</script>

<style scoped>
.panel { min-height:100vh; background:#f0f4f8; display:flex; flex-direction:column; }
.header { background:#1a3a6b; padding:12px 24px; display:flex; align-items:center; justify-content:space-between; }
.header-left { display:flex; align-items:center; gap:10px; }
.header-right { display:flex; align-items:center; gap:16px; }
.logo { width:180px; height:60px; object-fit:contain; }
.sistema-nombre { color:white; font-weight:bold; font-size:1.1em; }
.usuario-info { display:flex; align-items:center; gap:8px; }
.icono-perfil { width:20px; height:20px; }
.nombre-usuario { color:white; font-size:0.9rem; }
.btn-tema {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: white; padding: 6px 10px;
  border-radius: 6px; cursor: pointer; font-size: 1rem;
  transition: all 0.2s;
}
.btn-tema:hover { background: rgba(255,255,255,0.25); }
.btn-logout { background:transparent; border:1px solid white; color:white; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:0.85rem; transition:all 0.2s; }
.btn-logout:hover { background:white; color:#1a3a6b; }
.main { flex:1; padding:24px; max-width:1100px; margin:0 auto; width:100%; display:flex; flex-direction:column; gap:24px; }
.hero-section { display:grid; grid-template-columns:1fr auto; gap:24px; background:linear-gradient(135deg,#1a3a6b 0%,#2d6aa1 100%); border-radius:16px; padding:32px; color:white; align-items:center; }
@media(max-width:700px){.hero-section{grid-template-columns:1fr;}}
.saludo { font-size:1rem; opacity:0.8; margin:0 0 4px; text-transform:capitalize; }
.nombre-grande { font-size:2.2rem; font-weight:800; margin:0 0 4px; letter-spacing:-0.5px; }
.fecha-hoy { font-size:0.85rem; opacity:0.7; margin:0 0 20px; text-transform:capitalize; }
.frase-bloque { background:rgba(255,255,255,0.1); border-radius:10px; padding:14px 16px; border-left:3px solid rgba(255,255,255,0.4); max-width:500px; }
.comilla { font-size:1.5rem; opacity:0.5; line-height:1; }
.frase-texto { font-size:0.88rem; opacity:0.95; margin:4px 0; font-style:italic; line-height:1.5; }
.frase-autor { font-size:0.78rem; opacity:0.65; }
.clima-bloque { background:rgba(255,255,255,0.12); border-radius:14px; padding:20px 24px; display:flex; flex-direction:column; align-items:center; gap:8px; min-width:160px; }
.clima-loading { justify-content:center; min-height:120px; }
.clima-icono { font-size:2.8rem; line-height:1; }
.clima-datos { text-align:center; }
.clima-temp { font-size:1.8rem; font-weight:800; display:block; }
.clima-desc { font-size:0.8rem; opacity:0.8; display:block; }
.clima-lugar { font-size:0.72rem; opacity:0.6; display:block; }
.clima-extra { display:flex; gap:16px; margin-top:4px; }
.clima-extra-item { display:flex; flex-direction:column; align-items:center; gap:2px; }
.extra-label { font-size:0.7rem; opacity:0.7; }
.extra-val { font-size:0.82rem; font-weight:600; }
.clima-spinner { width:28px; height:28px; border:3px solid rgba(255,255,255,0.2); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin{to{transform:rotate(360deg);}}
.acciones-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
@media(max-width:700px){.acciones-grid{grid-template-columns:1fr;}}
.accion-card { background:white; border-radius:14px; padding:20px; display:flex; align-items:center; gap:16px; cursor:pointer; box-shadow:0 2px 8px rgba(0,0,0,0.06); transition:all 0.2s ease; border:2px solid transparent; }
.accion-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(26,58,107,0.15); border-color:#1a3a6b; }
.accion-principal { background:linear-gradient(135deg,#1a3a6b,#2d6aa1); color:white; }
.accion-principal .accion-info h3 { color:white; }
.accion-principal .accion-info p  { color:rgba(255,255,255,0.7); }
.accion-principal .accion-arrow   { color:rgba(255,255,255,0.8); }
.accion-icono-wrap { width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.accion-icono-wrap.azul    { background:rgba(255,255,255,0.15); }
.accion-icono-wrap.verde   { background:#f0fdf4; }
.accion-icono-wrap.naranja { background:#fff7ed; }
.accion-img   { width:36px; height:36px; object-fit:contain; border-radius:8px; }
.accion-emoji { font-size:1.6rem; }
.accion-info { flex:1; }
.accion-info h3 { font-size:0.95rem; font-weight:700; color:#1a3a6b; margin:0 0 2px; }
.accion-info p  { font-size:0.78rem; color:#6b7280; margin:0; }
.accion-arrow   { font-size:1.2rem; color:#9ca3af; flex-shrink:0; }
.inferior-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
@media(max-width:700px){.inferior-grid{grid-template-columns:1fr;}}
.calendario-card { background:white; border-radius:14px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.cal-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.cal-titulo { font-weight:700; color:#1a3a6b; font-size:0.95rem; }
.cal-nav { background:none; border:1px solid #e5e7eb; border-radius:6px; width:28px; height:28px; cursor:pointer; font-size:1rem; color:#1a3a6b; display:flex; align-items:center; justify-content:center; }
.cal-nav:hover { background:#f0f4f8; }
.cal-dias-semana { display:grid; grid-template-columns:repeat(7,1fr); margin-bottom:6px; }
.cal-dias-semana span { text-align:center; font-size:0.7rem; font-weight:700; color:#9ca3af; padding:4px 0; }
.cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:2px; }
.cal-dia { aspect-ratio:1; display:flex; align-items:center; justify-content:center; font-size:0.78rem; border-radius:6px; color:#374151; }
.cal-hoy { background:#1a3a6b !important; color:white !important; font-weight:800; border-radius:8px; }
.cal-feriado { background:#fef3c7; color:#b45309; font-weight:700; }
.cal-domingo { color:#ef4444; }
.cal-leyenda { display:flex; gap:16px; margin-top:12px; padding-top:10px; border-top:1px solid #f0f4f8; }
.leg-item { display:flex; align-items:center; gap:6px; font-size:0.72rem; color:#6b7280; }
.leg-dot { width:10px; height:10px; border-radius:3px; }
.leg-dot.hoy     { background:#1a3a6b; }
.leg-dot.feriado { background:#f59e0b; }
.estado-card { background:white; border-radius:14px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); display:flex; flex-direction:column; gap:16px; }
.estado-titulo { font-size:0.95rem; font-weight:700; color:#1a3a6b; margin:0; }
.estado-loading { color:#9ca3af; font-size:0.85rem; }
.estado-contenido { display:flex; flex-direction:column; gap:12px; }
.estado-fila { display:flex; align-items:center; gap:12px; padding:12px 14px; border-radius:10px; }
.estado-ok        { background:#f0fdf4; }
.estado-tarde     { background:#fefce8; }
.estado-pendiente { background:#f9fafb; }
.estado-icono { font-size:1.4rem; flex-shrink:0; }
.estado-texto { display:flex; flex-direction:column; gap:1px; }
.estado-label { font-size:0.72rem; color:#9ca3af; font-weight:600; text-transform:uppercase; }
.estado-valor { font-size:0.88rem; font-weight:600; color:#374151; }
.tiempo-hoy { display:flex; flex-direction:column; align-items:center; padding:14px; background:#eff6ff; border-radius:10px; gap:4px; margin-top:4px; }
.tiempo-label { font-size:0.75rem; color:#6b7280; }
.tiempo-valor { font-family:monospace; font-size:1.4rem; font-weight:800; color:#1a3a6b; }
</style>