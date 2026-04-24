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
          <div class="confirmacion-icono">{{ tipoMarcacion === 'ENTRADA' ? '🟢' : '🔴' }}</div>
          <h3>{{ tipoMarcacion === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida' }}</h3>
          <p class="fecha-texto">{{ fechaHora }}</p>

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

        <!-- Barra de intentos restantes -->
        <div v-if="intentosRestantes !== null" class="intentos-bar">
          <span class="intentos-label">Intentos restantes:</span>
          <span
            v-for="n in maxIntentos" :key="n"
            class="intento-dot"
            :class="n <= intentosRestantes ? 'dot-activo' : 'dot-usado'"
          ></span>
          <span class="intentos-num" :class="intentosRestantes <= 1 ? 'texto-rojo' : ''">
            {{ intentosRestantes }}
          </span>
        </div>

        <div class="camara-wrapper">
          <video ref="videoRef" autoplay playsinline class="video"></video>
          <div class="guia-rostro">
            <svg viewBox="0 0 320 320" class="guia-svg">
              <ellipse
                cx="160" cy="160" rx="100" ry="120"
                fill="none"
                stroke="rgba(3,221,83,0.8)"
                stroke-width="2.5"
                stroke-dasharray="8 4"
              />
            </svg>
          </div>
          <!-- Overlay de procesando -->
          <div v-if="detectando" class="overlay-procesando">
            <div class="spinner"></div>
            <span>Verificando...</span>
          </div>
          <canvas ref="canvasRef" style="display:none"></canvas>
        </div>

        <p class="instruccion" :class="instruccionClase">{{ mensajeEstado }}</p>

        <button
          @click="intentarMarcacion"
          :disabled="detectando"
          class="btn-capturar"
        >
          <span v-if="detectando">⏳ Procesando...</span>
          <span v-else>📸 Verificar rostro</span>
        </button>

        <div v-if="errorCamara" class="error-box">{{ errorCamara }}</div>
      </div>

      <!-- PASO 3: RESULTADO -->
      <div v-if="paso === 'resultado'" class="resultado-container">
        <div :class="['resultado-card', resultado.exito ? 'resultado-exito' : resultado.info ? 'resultado-info' : 'resultado-error']">
          <div class="resultado-icono">
            <img
              :src="resultado.exito ? iconoExito : resultado.info ? iconoExito : iconoError"
              :alt="resultado.exito ? 'Éxito' : 'Info'"
              class="img-resultado"
            />
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

          <div v-if="resultado.va_a_asistencia !== undefined" class="asistencia-badge"
               :class="resultado.va_a_asistencia ? 'badge-cuenta' : 'badge-no-cuenta'">
            {{ resultado.va_a_asistencia ? '✓ Registrada en asistencia' : 'ℹ Guardada solo en historial' }}
          </div>

          <div v-if="resultado.ubicacion && resultado.exito" class="ubicacion-resultado">
            <span class="ubi-icon">📍</span>
            <span class="ubi-txt">
              {{ resultado.ubicacion.ciudad || 'Red local' }}
              <span v-if="resultado.ubicacion.pais">, {{ resultado.ubicacion.pais }}</span>
            </span>
          </div>
        </div>

        <div class="resultado-botones">
          <button @click="$router.push('/trabajador/panel')" class="btn-si">
            Ir al panel
          </button>
          <button
            v-if="!resultado.exito && !resultado.info && !resultado.bloqueado"
            @click="reiniciar"
            class="btn-no"
          >
            Intentar de nuevo
          </button>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna   from '@/assets/icon-luna.svg'
import iconoSol    from '@/assets/icon-sol.svg'
import iconoExito  from '@/assets/icon-check.svg'
import iconoError  from '@/assets/icon-sin-marcar.svg'

import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore }  from '@/stores/auth'
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
const mensajeEstado = ref('Centre su rostro dentro del óvalo y presione el botón')
const instruccionClase = ref('')   // '' | 'instruccion-warn' | 'instruccion-error'
const paso          = ref('confirmar')
const tipoMarcacion = ref('ENTRADA')

// Intentos faciales
const intentosRestantes = ref(null)
const maxIntentos       = ref(5)

// Geo
const geoLatitud  = ref(null)
const geoLongitud = ref(null)
const geoEstado   = ref('obteniendo')

let stream = null

// ─── COMPUTED ──────────────────────────────────────────────────────────────
const fechaHora = computed(() => new Date().toLocaleString('es-PE', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  hour: '2-digit', minute: '2-digit'
}))

const geoTexto = computed(() => {
  const m = { obteniendo: 'Obteniendo ubicación...', ok: 'Ubicación obtenida',
               denegado: 'Permiso de ubicación denegado (opcional)',
               'no-soportado': 'Geolocalización no disponible en este dispositivo' }
  return m[geoEstado.value] || ''
})

const geoClase = computed(() => ({
  'geo-ok':       geoEstado.value === 'ok',
  'geo-denegado': geoEstado.value === 'denegado',
  'geo-cargando': geoEstado.value === 'obteniendo',
}))

// ─── LIFECYCLE ─────────────────────────────────────────────────────────────
onMounted(async () => {
  pedirGeolocalizacion()
  await verificarTipoMarcacion()
})

onUnmounted(() => {
  detenerCamara()
})

// ─── GEO ───────────────────────────────────────────────────────────────────
function pedirGeolocalizacion() {
  if (!navigator.geolocation) { geoEstado.value = 'no-soportado'; return }
  geoEstado.value = 'obteniendo'
  navigator.geolocation.getCurrentPosition(
    pos  => { geoLatitud.value = pos.coords.latitude; geoLongitud.value = pos.coords.longitude; geoEstado.value = 'ok' },
    ()   => { geoEstado.value = 'denegado' },
    { timeout: 8000, maximumAge: 60000 }
  )
}

// ─── VERIFICAR TIPO ─────────────────────────────────────────────────────────
async function verificarTipoMarcacion() {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const response     = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    const marcaciones  = response.data
    const hoy          = new Date().toLocaleDateString('es-PE')

    const hoyMarcaciones = marcaciones.filter(m => {
      const esHoy  = new Date(m.fecha).toLocaleDateString('es-PE') === hoy
      const afecta = m.va_a_asistencia === true
      return esHoy && afecta
    })

    const entradaHoy = hoyMarcaciones.find(m => m.tipo === 'ENTRADA_VALIDA' || m.tipo === 'ENTRADA')
    const salidaHoy  = hoyMarcaciones.find(m => m.tipo === 'SALIDA_VALIDA'  || m.tipo === 'SALIDA')

    if (entradaHoy && salidaHoy) {
      paso.value = 'resultado'
      resultado.value = {
        exito: false, info: true,
        mensaje: 'Ya registró su asistencia de entrada y salida de hoy.',
        va_a_asistencia: true,
      }
      return
    }

    const perfilResponse = await api.get('/api/auth/perfil/')
    if (perfilResponse.data.bloqueado) {
      paso.value = 'resultado'
      resultado.value = { exito: false, bloqueado: true, mensaje: 'Su cuenta está bloqueada. Contacte al administrador.' }
      return
    }

    tipoMarcacion.value = entradaHoy ? 'SALIDA' : 'ENTRADA'
    paso.value = 'confirmar'

  } catch {
    tipoMarcacion.value = 'ENTRADA'
    paso.value = 'confirmar'
  }
}

// ─── CONFIRMAR → CAMARA ─────────────────────────────────────────────────────
async function confirmar() {
  paso.value = 'camara'
  await iniciarCamara()
}

// ─── CÁMARA ─────────────────────────────────────────────────────────────────
async function iniciarCamara() {
  errorCamara.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 480 }
    })
    videoRef.value.srcObject = stream
  } catch {
    errorCamara.value = 'No se pudo acceder a la cámara. Verifique los permisos.'
  }
}

function detenerCamara() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

// ─── MARCACION ──────────────────────────────────────────────────────────────
async function intentarMarcacion() {
  if (detectando.value) return
  detectando.value = true
  instruccionClase.value = ''
  mensajeEstado.value    = 'Verificando identidad...'

  try {
    const canvas = canvasRef.value
    const video  = videoRef.value

    canvas.width  = video.videoWidth  || 640
    canvas.height = video.videoHeight || 480
    canvas.getContext('2d').drawImage(video, 0, 0)
    const imagenBase64 = canvas.toDataURL('image/jpeg', 0.95)

    const payload = {
      trabajador_id: auth.usuario?.trabajador_id,
      imagen:        imagenBase64,
      dispositivo:   navigator.userAgent.includes('Mobile') ? 'Móvil' : 'PC Oficina',
    }
    if (geoLatitud.value  !== null) payload.latitud  = geoLatitud.value
    if (geoLongitud.value !== null) payload.longitud = geoLongitud.value

    const response = await api.post('/api/reconocimiento/verificar/', payload)

    // ── ÉXITO ──────────────────────────────────────────────────────────────
    detenerCamara()

    const marcacion    = response.data.marcacion
    const ubicacion    = response.data.ubicacion || {}
    const mensaje      = response.data.mensaje || 'Marcación registrada'
    const vaAsistencia = response.data.va_a_asistencia ?? marcacion?.va_a_asistencia ?? false

    resultado.value = {
      exito: true,
      info:  !vaAsistencia,
      mensaje,
      tipo:   marcacion?.tipo === 'ENTRADA_VALIDA' ? 'ENTRADA'
            : marcacion?.tipo === 'SALIDA_VALIDA'  ? 'SALIDA'
            : marcacion?.tipo,
      estado:          marcacion?.estado,
      hora:            marcacion?.fecha
                       ? new Date(marcacion.fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
                       : null,
      va_a_asistencia: vaAsistencia,
      ubicacion,
    }
    paso.value = 'resultado'

  } catch (e) {
    detectando.value = false

    const errorMsg   = e.response?.data?.error   || ''
    const httpStatus = e.response?.status

    // ── 1. Sin respuesta del servidor / red ─────────────────────────────────
    if (!e.response) {
      setMensajeError('Sin conexión con el servidor. Verifique su red e intente de nuevo.')
      return
    }

    // ── 2. Sin rostro detectado / baja calidad / múltiples rostros ───────────
    const esSinRostro = errorMsg.toLowerCase().includes('no se detectó')
                     || errorMsg.toLowerCase().includes('no se pudo detectar')
                     || errorMsg.toLowerCase().includes('calidad')
                     || errorMsg.toLowerCase().includes('baja calidad')
    const esMasDeUnRostro = errorMsg.toLowerCase().includes('más de un rostro')
                         || errorMsg.toLowerCase().includes('mas de un rostro')

    if (esMasDeUnRostro) {
      setMensajeError('⚠️ Se detectaron varias personas. Asegúrese de estar solo frente a la cámara.')
      return
    }

    if (esSinRostro) {
      setMensajeError('No se detectó rostro. Acérquese, mejore la iluminación y presione de nuevo.')
      return
    }

    // ── 3. Falta embedding del trabajador ────────────────────────────────────
    const sinEmbedding = errorMsg.toLowerCase().includes('no tiene embedding')
                      || errorMsg.toLowerCase().includes('embedding registrado')
    if (sinEmbedding) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = {
        exito: false,
        mensaje: 'Su rostro aún no ha sido registrado en el sistema. Comuníquese con el administrador para que registre su perfil facial.',
      }
      return
    }

    // ── 4. IP no autorizada ──────────────────────────────────────────────────
    if (httpStatus === 403 && (errorMsg.toLowerCase().includes('ip') || errorMsg.toLowerCase().includes('red'))) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = {
        exito: false,
        mensaje: 'No puede marcar desde esta red. Conéctese a la red autorizada de la Municipalidad.',
      }
      return
    }

    // ── 5. Usuario bloqueado (403 general) ───────────────────────────────────
    if (httpStatus === 403) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = {
        exito: false, bloqueado: true,
        mensaje: errorMsg.includes('bloqueado')
          ? 'Usuario bloqueado por intentos fallidos. Contacte al administrador.'
          : errorMsg,
      }
      return
    }

    // ── 6. Rostro no coincide (401) ──────────────────────────────────────────
    if (httpStatus === 401 || errorMsg.toLowerCase().includes('no coincide')) {
      const match     = errorMsg.match(/Intentos restantes:\s*(\d+)/i)
      const restantes = match ? parseInt(match[1]) : null

      if (restantes !== null) {
        intentosRestantes.value = restantes
      }

      if (restantes === 0 || errorMsg.toLowerCase().includes('bloqueado')) {
        detenerCamara()
        paso.value = 'resultado'
        resultado.value = {
          exito: false, bloqueado: true,
          mensaje: 'Usuario bloqueado por demasiados intentos fallidos. Contacte al administrador.',
        }
        return
      }

      if      (restantes >= 4) setMensajeError('Rostro no coincide. Posiciónese bien frente a la cámara.')
      else if (restantes === 3) setMensajeError('No coincide. Acérquese más y mejore la iluminación.')
      else if (restantes === 2) setMensajeError('⚠️ No coincide. Mire de frente con buena luz. Quedan pocos intentos.')
      else if (restantes === 1) setMensajeError('🚨 Último intento — si falla, su cuenta será bloqueada.')
      else                      setMensajeError('Rostro no coincide. Intente de nuevo.')

      return
    }

    // ── 7. Trabajador inactivo ────────────────────────────────────────────────
    if (httpStatus === 403 && errorMsg.toLowerCase().includes('inactivo')) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'Su cuenta se encuentra inactiva. Contacte al administrador.' }
      return
    }

    // ── 8. Error 500 ──────────────────────────────────────────────────────────
    if (httpStatus === 500) {
      setMensajeError('Error en el servidor. Espere un momento e intente de nuevo.')
      return
    }

    // ── 9. Cualquier otro error ───────────────────────────────────────────────
    setMensajeError(errorMsg || 'Error al procesar. Intente de nuevo.')
  }
}

// ─── HELPERS ────────────────────────────────────────────────────────────────
function setMensajeError(msg) {
  mensajeEstado.value    = msg
  instruccionClase.value = 'instruccion-error'
}

function reiniciar() {
  resultado.value        = null
  errorCamara.value      = ''
  mensajeEstado.value    = 'Centre su rostro dentro del óvalo y presione el botón'
  instruccionClase.value = ''
  intentosRestantes.value = null
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
  --bg-main:    #141416cc;
  --bg-card:    #141416;
  --bg-soft:    rgba(255,255,255,0.08);
  --text-main:  #fcfcfd;
  --text-soft:  rgba(255,255,255,0.6);
  --border-color: #232327;
  --accent:     #18c440;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-main);
  color: var(--text-main);
}

/* ── TEMA CLARO ── */
.panel.light {
  --bg-main:    #f8fafc;
  --bg-card:    #ffffff;
  --bg-soft:    #f1f5f9;
  --text-main:  #0f172a;
  --text-soft:  #64748b;
  --border-color: #e2e8f0;
  --accent:     #2563eb;
}

/* ── HEADER ── */
.header-bar {
  position: relative; z-index: 10;
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 28px;
  border-bottom: 2px solid var(--accent);
  background: var(--bg-card);
}
.header-left { display: flex; align-items: center; gap: 10px; }
.header-right { display: flex; align-items: center; gap: 10px; }
.logo { width: 150px; height: 50px; object-fit: contain; }
.sistema-nombre { color: var(--text-main); font-weight: 600; font-size: 0.95rem; opacity: 0.9; }
.nombre-chip {
  display: flex; align-items: center; gap: 6px;
  color: var(--text-main); font-size: 0.82rem;
  background: var(--bg-soft); padding: 9px 14px;
  border-radius: 6px; border: 1px solid var(--border-color);
}
.icono-perfil { width: 18px; height: 18px; }
.btn-sm {
  display: flex; align-items: center; justify-content: center;
  padding: 5px 25px; cursor: pointer;
  background: var(--bg-soft); border: 1px solid var(--border-color); border-radius: 4px;
}
.btn-sm:hover { background: var(--accent); }
.icono-btn { width: 18px; height: 18px; display: block; }
.btn-logout {
  background: red; border: 1px solid rgba(255,255,255,0.35);
  color: #ffffff; padding: 9px 42px; border-radius: 6px; cursor: pointer; font-size: 0.82rem;
}
.btn-logout:hover { background: #000; color: #ff0000; }
.panel.light .header-bar { background: white; border-bottom: 1px solid var(--border-color); }

/* ── CONTENT ── */
.content {
  position: relative; z-index: 10; flex: 1;
  padding: 28px 32px 24px;
  display: flex; flex-direction: column; gap: 24px;
  background-color: var(--bg-main); color: var(--text-main);
}

/* ── TÍTULO ── */
.titulo-seccion { display: flex; align-items: center; gap: 16px; }
.btn-volver {
  background: var(--bg-soft); border: 1px solid var(--border-color);
  color: var(--text-main); font-size: 0.9rem; font-weight: 600;
  padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease;
}
.btn-volver:hover { border-color: var(--accent); color: var(--accent); }
h2 { font-size: 1.3rem; font-weight: 700; color: var(--text-main); margin: 0; }

/* ── CONFIRMACIÓN ── */
.confirmacion-container {
  display: flex; justify-content: center; align-items: flex-start; padding-top: 20px;
}
.confirmacion-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 16px; padding: 40px 48px;
  text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  max-width: 420px; width: 100%;
}
.confirmacion-icono { font-size: 3.5rem; margin-bottom: 12px; }
.confirmacion-card h3 { font-size: 1.3rem; font-weight: 700; color: var(--text-main); margin-bottom: 6px; }
.fecha-texto { font-size: 0.85rem; color: var(--text-soft); margin-bottom: 12px; text-transform: capitalize; }
.confirmacion-pregunta { font-size: 1rem; color: var(--text-main); margin: 20px 0 24px; }
.confirmacion-botones { display: flex; gap: 16px; justify-content: center; }

/* ── BOTONES ── */
.btn-si {
  padding: 12px 32px; background: var(--accent); color: white; border: none;
  border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.2s ease;
}
.btn-si:hover { opacity: 0.88; transform: translateY(-1px); }
.btn-no {
  padding: 12px 32px; background: var(--bg-soft); color: var(--text-soft);
  border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer;
  font-size: 1rem; transition: all 0.2s ease;
}
.btn-no:hover { border-color: var(--text-soft); color: var(--text-main); }

/* ── GEO ── */
.geo-status {
  display: inline-flex; align-items: center; gap: 6px; font-size: 0.78rem;
  padding: 5px 14px; border-radius: 20px; margin-bottom: 12px;
  background: var(--bg-soft); color: var(--text-soft); border: 1px solid var(--border-color);
}
.geo-ok       { background: rgba(24,196,64,0.1);   color: #18c440; border-color: rgba(24,196,64,0.3); }
.geo-denegado { background: rgba(251,191,36,0.1);  color: #d97706; border-color: rgba(251,191,36,0.3); }
.geo-cargando { background: rgba(59,130,246,0.1);  color: #3b82f6; border-color: rgba(59,130,246,0.3); }
.geo-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; background: currentColor; opacity: 0.8; }

/* ── INTENTOS ── */
.intentos-bar {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.82rem; color: var(--text-soft);
  width: 100%; max-width: 420px;
}
.intentos-label { margin-right: 4px; }
.intento-dot {
  width: 12px; height: 12px; border-radius: 50%;
  transition: background 0.3s;
}
.dot-activo { background: #18c440; }
.dot-usado  { background: rgba(239,68,68,0.5); }
.intentos-num { margin-left: 4px; font-weight: 700; }
.texto-rojo   { color: #ef4444; }

/* ── CÁMARA ── */
.camara-container { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.camara-wrapper {
  position: relative; width: 100%; max-width: 420px;
  border-radius: 14px; overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4); border: 1px solid var(--border-color); background: #000;
}
.video { width: 100%; display: block; aspect-ratio: 4/3; transform: scaleX(-1); object-fit: cover; }

/* Overlay procesando */
.overlay-procesando {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 12px; color: #fff; font-size: 1rem; font-weight: 600;
}
.spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: #18c440;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.guia-rostro {
  position: absolute; inset: 0; pointer-events: none;
  display: flex; align-items: center; justify-content: center;
}
.guia-svg { width: 90%; height: 90%; opacity: 0.9; }

.instruccion {
  font-size: 0.9em; color: var(--text-soft);
  text-align: center; max-width: 420px; line-height: 1.5;
  transition: color 0.2s;
}
.instruccion-error { color: #ef4444 !important; font-weight: 600; }
.instruccion-warn  { color: #d97706 !important; }

.btn-capturar {
  padding: 14px; background: var(--accent); color: white; border: none;
  border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease; width: 100%; max-width: 420px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.btn-capturar:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.btn-capturar:disabled { opacity: 0.5; cursor: not-allowed; background: #6b7280; }

.error-box {
  background: rgba(239,68,68,0.1); color: #ef4444;
  border: 1px solid rgba(239,68,68,0.3); padding: 12px 16px;
  border-radius: 10px; text-align: center;
  width: 100%; max-width: 420px; font-size: 0.9rem;
}
.panel.light .error-box { background: #fef2f2; color: #dc2626; border-color: #fecaca; }

/* ── RESULTADO ── */
.resultado-container { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.resultado-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 16px; padding: 40px 48px;
  text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  width: 100%; max-width: 420px;
}
.resultado-exito  { border-top: 4px solid #18c440; }
.resultado-info   { border-top: 4px solid #f59e0b; }
.resultado-error  { border-top: 4px solid #ef4444; }

.resultado-icono { display: flex; justify-content: center; align-items: center; margin-bottom: 16px; }
.img-resultado   { width: 80px; height: 80px; object-fit: contain; }
.resultado-card h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 12px; }
.res-dato          { color: var(--text-soft); font-size: 0.9rem; margin: 6px 0; }
.res-dato strong   { color: var(--text-main); }
.texto-verde       { color: #18c440 !important; }
.texto-amarillo    { color: #d97706 !important; }

.asistencia-badge {
  display: inline-block; margin: 12px auto 0;
  padding: 5px 16px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;
}
.badge-cuenta    { background: rgba(24,196,64,0.15); color: #18c440; border: 1px solid rgba(24,196,64,0.3); }
.badge-no-cuenta { background: rgba(251,191,36,0.15); color: #d97706; border: 1px solid rgba(251,191,36,0.3); }
.panel.light .badge-cuenta    { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.panel.light .badge-no-cuenta { background: #fef9c3; color: #854d0e; border-color: #fde68a; }

.ubicacion-resultado {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 14px;
  padding: 6px 14px; background: rgba(24,196,64,0.1);
  border: 1px solid rgba(24,196,64,0.25); border-radius: 20px;
  font-size: 0.82rem; color: #18c440;
}
.panel.light .ubicacion-resultado { background: #f0fdf4; color: #166534; border-color: #bbf7d0; }
.ubi-icon { font-size: 0.9rem; }

.resultado-botones { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .header-bar { flex-direction: column; align-items: flex-start; gap: 10px; padding: 12px 16px; }
  .header-right { width: 100%; justify-content: space-between; }
  .logo { width: 110px; height: auto; }
  .sistema-nombre { font-size: 0.8rem; }
  .nombre-chip { padding: 6px 10px; font-size: 0.75rem; }
  .btn-logout { padding: 6px 12px; font-size: 0.75rem; }
  .content { padding: 16px; gap: 16px; }
  h2 { font-size: 1.1rem; }
  .confirmacion-card { padding: 28px 20px; }
  .confirmacion-card h3 { font-size: 1.1rem; }
  .confirmacion-botones { flex-direction: column-reverse; gap: 10px; }
  .btn-si, .btn-no { width: 100%; padding: 14px; }
  .btn-capturar { padding: 14px; font-size: 0.95rem; }
  .resultado-card { padding: 28px 20px; }
  .resultado-botones { flex-direction: column; width: 100%; max-width: 420px; }
  .resultado-botones .btn-si,
  .resultado-botones .btn-no { width: 100%; }
}
</style>