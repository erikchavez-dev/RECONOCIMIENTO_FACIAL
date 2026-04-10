<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <!-- HEADER -->
    <header class="header-bar">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-chip">
          <img :src="iconoPerfil" class="icono-perfil" />
          {{ auth.usuario?.nombre_completo }}
        </span>
        <button @click="theme.toggle()" class="btn-sm" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">
          <img :src="theme.oscuro ? iconoSol : iconoLuna" alt="Icono Tema" class="icono-btn" />
        </button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="content">
      <div class="titulo-seccion">
        <button @click="volver" class="btn-volver">← Volver</button>
        <h2>Marcar Asistencia</h2>
      </div>

      <!-- PASO 1: CONFIRMACIÓN -->
      <div v-if="paso === 'confirmar'" class="confirmacion-container">
        <div class="confirmacion-card">
          <div class="confirmacion-icono">{{ tipoMarcacion === 'ENTRADA' ? '' : '' }}</div>
          <h3>{{ tipoMarcacion === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida' }}</h3>
          <p class="fecha-texto">{{ fechaHora }}</p>

          <!-- Indicador de geolocalización -->
          <div class="geo-status" :class="geoClase">
            <span class="geo-dot"></span>
            <span class="geo-txt">{{ geoTexto }}</span>
          </div>

          <p class="confirmacion-pregunta">
            ¿Desea registrar su <strong>{{ tipoMarcacion === 'ENTRADA' ? 'entrada' : 'salida' }}</strong> ahora?
          </p>
          <div class="confirmacion-botones">
            <button @click="volver" class="btn-no">No</button>
            <button @click="confirmar" class="btn-si">Sí, registrar</button>
          </div>
        </div>
      </div>

      <!-- PASO 2: CÁMARA -->
      <div v-if="paso === 'camara'" class="camara-container">
        <div class="camara-wrapper">
          <video ref="videoRef" autoplay playsinline class="video"></video>
          <div class="guia-rostro">
            <svg viewBox="0 0 300 300" class="guia-svg">
              <ellipse
                cx="160" cy="160" rx="95" ry="115"
                fill="none"
                stroke="rgba(3, 221, 83, 0.8)"
                stroke-width="2.5"
                stroke-dasharray="8 4"
              />
            </svg>
          </div>
          <canvas ref="canvasRef" style="display:none"></canvas>
        </div>

        <p class="instruccion">{{ mensajeEstado }}</p>

        <button @click="intentarMarcacion" :disabled="detectando" class="btn-capturar">
          {{ detectando ? 'Procesando...' : 'Verificar rostro' }}
        </button>

        <div v-if="errorCamara" class="error-box">{{ errorCamara }}</div>
      </div>

      <!-- PASO 3: RESULTADO -->
      <div v-if="paso === 'resultado'" class="resultado-container">
        <div :class="['resultado-card', resultado.exito ? 'resultado-exito' : 'resultado-error']">
         <div class="resultado-icono">
            <img :src="resultado.exito ? iconoExito : iconoError" :alt="resultado.exito ? 'Éxito' : 'Error'"
              class="img-resultado" />
          </div>
          <h3>{{ resultado.mensaje }}</h3>
          <p v-if="resultado.tipo" class="res-dato">Tipo: <strong>{{ resultado.tipo }}</strong></p>
          <p v-if="resultado.estado" class="res-dato">
            Estado:
            <strong :class="resultado.estado === 'PUNTUAL' ? 'texto-verde' : 'texto-amarillo'">
              {{ resultado.estado }}
            </strong>
          </p>
          <p v-if="resultado.hora" class="res-dato">Hora: <strong>{{ resultado.hora }}</strong></p>

          <div v-if="resultado.ubicacion && resultado.exito" class="ubicacion-resultado">
            <span class="ubi-icon"></span>
            <span class="ubi-txt">
              {{ resultado.ubicacion.ciudad || 'Red local' }}
              <span v-if="resultado.ubicacion.pais">, {{ resultado.ubicacion.pais }}</span>
            </span>
          </div>
        </div>

        <div class="resultado-botones">
          <button v-if="resultado.exito" @click="$router.push('/trabajador/panel')" class="btn-si">
            Ir al panel
          </button>
          <button
            v-if="!resultado.exito && !resultado.mensaje.includes('entrada y salida')"
            @click="reiniciar"
            class="btn-si"
          >
            Intentar de nuevo
          </button>
          <button v-if="!resultado.exito" @click="$router.push('/trabajador/panel')" class="btn-no">
            Ir al panel
          </button>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna from '@/assets/icon-luna.svg'
import iconoSol from '@/assets/icon-sol.svg'
import iconoExito from '@/assets/icon-check.svg'
import iconoError from '@/assets/icon-sin-marcar.svg'


import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const router = useRouter()
const auth   = useAuthStore()
const theme  = useThemeStore()

const videoRef      = ref(null)
const canvasRef     = ref(null)
const detectando    = ref(false)
const resultado     = ref(null)
const errorCamara   = ref('')
const mensajeEstado = ref('Centre su rostro frente a la cámara y presione el botón')
const paso          = ref('confirmar')
const tipoMarcacion = ref('ENTRADA')

const geoLatitud  = ref(null)
const geoLongitud = ref(null)
const geoEstado   = ref('obteniendo')

let stream = null

const fechaHora = computed(() => {
  return new Date().toLocaleString('es-PE', {
    weekday: 'long', year: 'numeric',
    month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
})

const geoTexto = computed(() => {
  switch (geoEstado.value) {
    case 'obteniendo':   return 'Obteniendo ubicación...'
    case 'ok':           return 'Ubicación obtenida'
    case 'denegado':     return 'Permiso de ubicación denegado (opcional)'
    case 'no-soportado': return 'Geolocalización no disponible en este dispositivo'
    default:             return ''
  }
})

const geoClase = computed(() => ({
  'geo-ok':       geoEstado.value === 'ok',
  'geo-denegado': geoEstado.value === 'denegado',
  'geo-cargando': geoEstado.value === 'obteniendo',
}))

onMounted(async () => {
  pedirGeolocalizacion()
  await verificarTipoMarcacion()
})

onUnmounted(() => {
  detenerCamara()
})

function pedirGeolocalizacion() {
  if (!navigator.geolocation) { geoEstado.value = 'no-soportado'; return }
  geoEstado.value = 'obteniendo'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      geoLatitud.value  = pos.coords.latitude
      geoLongitud.value = pos.coords.longitude
      geoEstado.value   = 'ok'
    },
    () => { geoEstado.value = 'denegado' },
    { timeout: 8000, maximumAge: 60000 }
  )
}

async function verificarTipoMarcacion() {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const response     = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    const marcaciones  = response.data

    const hoy = new Date().toLocaleDateString('es-PE')
    const hoyMarcaciones = marcaciones.filter(m =>
      new Date(m.fecha).toLocaleDateString('es-PE') === hoy
    )

    const entradaHoy = hoyMarcaciones.find(m => m.tipo === 'ENTRADA')
    const salidaHoy  = hoyMarcaciones.find(m => m.tipo === 'SALIDA')

    if (entradaHoy && salidaHoy) {
      paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'Ya registró su asistencia de entrada y salida de hoy' }
      return
    }

    const perfilResponse = await api.get('/api/auth/perfil/')
    if (perfilResponse.data.bloqueado) {
      paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'Su cuenta está bloqueada. Contacte al administrador.' }
      return
    }

    tipoMarcacion.value = entradaHoy ? 'SALIDA' : 'ENTRADA'
    paso.value = 'confirmar'

  } catch (e) {
    tipoMarcacion.value = 'ENTRADA'
    paso.value = 'confirmar'
  }
}

async function confirmar() {
  paso.value = 'camara'
  await iniciarCamara()
}

async function iniciarCamara() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' , width: 640, height: 480 }
    }) 
    videoRef.value.srcObject = stream
  } catch (e) {
    errorCamara.value = 'No se pudo acceder a la cámara. Verifique los permisos.'
  }
}

function detenerCamara() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

async function intentarMarcacion() {
  if (detectando.value) return
  detectando.value = true
  mensajeEstado.value = 'Verificando...'

  try {
    const canvas = canvasRef.value
    const video  = videoRef.value
    canvas.width  = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    const imagenBase64 = canvas.toDataURL('image/jpeg', 0.95)

    const payload = {
      trabajador_id: auth.usuario?.trabajador_id,
      imagen:        imagenBase64,
      dispositivo:   navigator.userAgent.includes('Mobile') ? 'Móvil' : 'PC Oficina',
    }

    if (geoLatitud.value !== null)  payload.latitud  = geoLatitud.value
    if (geoLongitud.value !== null) payload.longitud = geoLongitud.value

    const response = await api.post('/api/reconocimiento/verificar/', payload)

    detenerCamara()
    const marcacion = response.data.marcacion
    const ubicacion = response.data.ubicacion || {}

    resultado.value = {
      exito:    true,
      mensaje:  `${marcacion.tipo === 'ENTRADA' ? 'Entrada' : 'Salida'} registrada correctamente`,
      tipo:     marcacion.tipo,
      estado:   marcacion.estado,
      hora:     new Date(marcacion.fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' }),
      ubicacion,
    }
    paso.value = 'resultado'

  } catch (e) {
    const errorMsg   = e.response?.data?.error || ''
    const httpStatus = e.response?.status

    if (!e.response || errorMsg.includes('no se detectó') ||
        errorMsg.includes('calidad') || errorMsg.includes('No se detectó')) {
      mensajeEstado.value = 'No se detectó rostro. Acérquese más, mejore la iluminación y presione de nuevo.'
      detectando.value = false
      return
    }

    if (errorMsg.includes('entrada y salida')) {
      detenerCamara()
      resultado.value = { exito: false, mensaje: 'Ya registró su asistencia de entrada y salida de hoy' }
      paso.value = 'resultado'
      return
    }

    if (httpStatus === 403) {
      detenerCamara()
      resultado.value = {
        exito: false,
        mensaje: errorMsg.toLowerCase().includes('ip') || errorMsg.toLowerCase().includes('red')
          ? 'No puede marcar desde esta red. Conéctese a la red autorizada de la Municipalidad.'
          : errorMsg.includes('bloqueado')
            ? 'Usuario bloqueado por intentos fallidos. Contacte al administrador.'
            : errorMsg,
      }
      paso.value = 'resultado'
      return
    }

    if (errorMsg.includes('no coincide') || httpStatus === 401) {
      const match     = errorMsg.match(/Intentos restantes: (\d+)/)
      const restantes = match ? parseInt(match[1]) : null

      if (restantes === null || restantes >= 4) {
        mensajeEstado.value = 'Rostro no coincide. Posiciónese bien y presione de nuevo.'
      } else if (restantes === 3) {
        mensajeEstado.value = 'Acérquese más a la cámara y mejore la iluminación.'
      } else if (restantes === 2) {
        mensajeEstado.value = 'Mire de frente con buena iluminación.'
      } else if (restantes === 1) {
        mensajeEstado.value = 'Último intento — si falla será bloqueado.'
      } else {
        detenerCamara()
        resultado.value = {
          exito: false,
          mensaje: 'No se pudo verificar su identidad. Contacte al administrador.'
        }
        paso.value = 'resultado'
      }
      detectando.value = false
      return
    }

    if (errorMsg.includes('horario') || errorMsg.includes('Fuera')) {
      detenerCamara()
      resultado.value = { exito: false, mensaje: errorMsg }
      paso.value = 'resultado'
      return
    }

    mensajeEstado.value = 'Error al procesar. Intente de nuevo.'
    detectando.value = false
  }
}

function reiniciar() {
  resultado.value     = null
  errorCamara.value   = ''
  mensajeEstado.value = 'Centre su rostro frente a la cámara y presione el botón'
  verificarTipoMarcacion()
}

function volver() {
  detenerCamara()
  router.push('/trabajador/panel')
}

async function handleLogout() {
  detenerCamara()
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── BASE / TEMA OSCURO ── */
.panel {
  --bg-main: #141416cc;
  --bg-card: #141416;
  --bg-soft: rgba(255,255,255,0.08);
  --text-main: #fcfcfd;
  --text-soft: rgba(255,255,255,0.6);
  --border-color: #232327;
  --accent: #18c440;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-main);
  color: var(--text-main);
}

/* ── TEMA CLARO ── */
.panel.light {
  --bg-main: #f8fafc;
  --bg-card: #ffffff;
  --bg-soft: #f1f5f9;
  --text-main: #0f172a;
  --text-soft: #64748b;
  --border-color: #e2e8f0;
  --accent: #2563eb;
}

/* ── HEADER ── */
.header-bar {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 28px;
  border-bottom: 2px solid var(--accent);
  background: var(--bg-card);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo {
  width: 150px;
  height: 50px;
  object-fit: contain;
}
.sistema-nombre {
  color: var(--text-main);
  font-weight: 600;
  font-size: 0.95rem;
  opacity: 0.9;
}
.nombre-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-main);
  font-size: 0.82rem;
  background: var(--bg-soft);
  padding: 9px 14px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}
.icono-perfil {
  width: 18px;
  height: 18px;
}
.btn-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 25px;
  cursor: pointer;
  background: var(--bg-soft);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}
.btn-sm:hover {
  background: var(--accent);
}
.icono-btn {
  width: 18px;
  height: 18px;
  display: block;
}
.btn-logout {
  background: red;
  border: 1px solid rgba(255,255,255,0.35);
  color: #ffffff;
  padding: 9px 42px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
}
.btn-logout:hover {
  background: #000000;
  color: #ff0000;
}

/* ── TEMA CLARO: header overrides ── */
.panel.light .nombre-chip {
  color: var(--text-main);
}
.panel.light .btn-sm {
  background: var(--bg-soft);
  border-color: var(--border-color);
}
.panel.light .btn-sm:hover {
  background: var(--accent);
}
.panel.light .header-bar {
  background: white;
  border-bottom: 1px solid var(--border-color);
}

/* ── CONTENT ── */
.content {
  position: relative;
  z-index: 10;
  flex: 1;
  padding: 28px 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: var(--bg-main);
  color: var(--text-main);
}

/* ── TÍTULO ── */
.titulo-seccion {
  display: flex;
  align-items: center;
  gap: 16px;
}
.btn-volver {
  background: var(--bg-soft);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  font-size: 0.9rem;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-volver:hover {
  border-color: var(--accent);
  color: var(--accent);
}
h2 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

/* ── CONFIRMACIÓN ── */
.resultado-icono {
  display: flex;
  justify-content: center;
  align-items: center;
}

.img-resultado {
  width: 80px;  
  height: 80px;
  object-fit: contain;
}


.confirmacion-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20px;
}
.confirmacion-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 40px 48px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  max-width: 420px;
  width: 100%;
}
.confirmacion-icono {
  font-size: 3.5rem;
  margin-bottom: 12px;
}
.confirmacion-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 6px;
}
.fecha-texto {
  font-size: 0.85rem;
  color: var(--text-soft);
  margin-bottom: 12px;
  text-transform: capitalize;
}
.confirmacion-pregunta {
  font-size: 1rem;
  color: var(--text-main);
  margin: 20px 0 24px;
}
.confirmacion-botones {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* ── BOTONES PRINCIPALES ── */
.btn-si {
  padding: 12px 32px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}
.btn-si:hover {
  opacity: 0.88;
  transform: translateY(-1px);
}
.btn-no {
  padding: 12px 32px;
  background: var(--bg-soft);
  color: var(--text-soft);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}
.btn-no:hover {
  border-color: var(--text-soft);
  color: var(--text-main);
}

/* ── GEOLOCALIZACIÓN ── */
.geo-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  padding: 5px 14px;
  border-radius: 20px;
  margin-bottom: 12px;
  background: var(--bg-soft);
  color: var(--text-soft);
  border: 1px solid var(--border-color);
}
.geo-ok {
  background: rgba(24, 196, 64, 0.1);
  color: #18c440;
  border-color: rgba(24, 196, 64, 0.3);
}
.geo-denegado {
  background: rgba(251, 191, 36, 0.1);
  color: #d97706;
  border-color: rgba(251, 191, 36, 0.3);
}
.geo-cargando {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.3);
}
.geo-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  background: currentColor;
  opacity: 0.8;
}

/* tema claro: geo */
.panel.light .geo-ok {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}
.panel.light .geo-denegado {
  background: #fef9c3;
  color: #854d0e;
  border-color: #fde68a;
}
.panel.light .geo-cargando {
  background: #dbeafe;
  color: #1e40af;
  border-color: #bfdbfe;
}

/* ── CÁMARA ── */
.camara-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.camara-wrapper {
  position: relative;
  width: 100%;
  max-width: 420px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  border: 1px solid var(--border-color);
  background: #000;
}
.video {
  width: 100%;
  display: block;
  aspect-ratio: 4/3;
  transform: scaleX(-1);
  object-fit: cover;
}
.guia-rostro {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
.guia-svg {
  width: 90%;
  height: 90%;
  opacity: 0.9;
}
.instruccion {
  font-size: 0.9em;
  color: var(--text-soft);
  text-align: center;
  max-width: 420px;
  line-height: 1.5;
}
.btn-capturar {
  padding: 14px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.btn-capturar:hover:not(:disabled) {
  opacity: 0.88;
  transform: translateY(-1px);
}
.btn-capturar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error-box {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 12px 16px;
  border-radius: 10px;
  text-align: center;
  width: 100%;
  max-width: 420px;
  font-size: 0.9rem;
}
.panel.light .error-box {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

/* ── RESULTADO ── */
.resultado-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.resultado-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 40px 48px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 420px;
}
.resultado-exito {
  border-top: 4px solid #18c440;
}
.resultado-error {
  border-top: 4px solid #ef4444;
}
.resultado-icono {
  font-size: 3.5rem;
  margin-bottom: 16px;
}
.resultado-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 12px;
}
.res-dato {
  color: var(--text-soft);
  font-size: 0.9rem;
  margin: 6px 0;
}
.res-dato strong {
  color: var(--text-main);
}
.texto-verde   { color: #18c440 !important; }
.texto-amarillo { color: #d97706 !important; }

.ubicacion-resultado {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  padding: 6px 14px;
  background: rgba(24, 196, 64, 0.1);
  border: 1px solid rgba(24, 196, 64, 0.25);
  border-radius: 20px;
  font-size: 0.82rem;
  color: #18c440;
}
.panel.light .ubicacion-resultado {
  background: #f0fdf4;
  color: #166534;
  border-color: #bbf7d0;
}
.ubi-icon { font-size: 0.9rem; }

.resultado-botones {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {

  /* HEADER */
  .header-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 16px;
  }
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  .logo {
    width: 110px;
    height: auto;
  }
  .sistema-nombre {
    font-size: 0.8rem;
  }
  .nombre-chip {
    padding: 6px 10px;
    font-size: 0.75rem;
  }
  .btn-logout {
    padding: 6px 12px;
    font-size: 0.75rem;
  }

  /* CONTENT */
  .content {
    padding: 16px;
    gap: 16px;
  }

  /* TÍTULO */
  .titulo-seccion {
    gap: 10px;
  }
  h2 {
    font-size: 1.1rem;
  }

  /* CONFIRMACIÓN */
  .confirmacion-card {
    padding: 28px 20px;
  }
  .confirmacion-card h3 {
    font-size: 1.1rem;
  }
  .confirmacion-botones {
    flex-direction: column;
    flex-direction: column-reverse;
    gap: 10px;
  }
  .btn-si,
  .btn-no {
    width: 100%;
    padding: 14px;
  }

  /* CÁMARA */
  .camara-wrapper {
    border-radius: 10px;
  }
  .btn-capturar {
    padding: 14px;
    font-size: 0.95rem;
  }

  /* RESULTADO */
  .resultado-card {
    padding: 28px 20px;
  }
  .resultado-botones {
    flex-direction: column;
    width: 100%;
    max-width: 420px;
  }
  .resultado-botones .btn-si,
  .resultado-botones .btn-no {
    width: 100%;
    justify-content: center;
  }
}
</style>