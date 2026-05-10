<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <!-- HEADER -->
    <AppHeader :antes-de-logout="detenerCamara" />

    <main class="content">
      <div class="titulo-seccion">
        <button @click="volver" class="btn-volver">← Volver</button>
        <h2>Marcar Asistencia</h2>
      </div>

      <!-- PASO: CÁMARA -->
      <div v-if="paso === 'camara'" class="camara-container">

        <!-- Aviso de pocos intentos (solo cuando quedan 2 o menos) -->
        <div v-if="intentosRestantes !== null && intentosRestantes <= 2" class="alerta-intentos"
             :class="intentosRestantes === 1 ? 'alerta-critica' : 'alerta-advertencia'">
          <span class="alerta-icono">{{ intentosRestantes === 1 ? '🚨' : '⚠️' }}</span>
          <span class="alerta-texto">
            {{ intentosRestantes === 1
              ? 'Último intento — si falla, su cuenta será bloqueada'
              : 'Solo quedan 2 intentos antes del bloqueo' }}
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
          <canvas ref="canvasRef" style="display:none"></canvas>
        </div>

        <!-- Mensaje de estado mejorado -->
        <div class="mensaje-estado-wrapper" :class="estadoClase">
          <span class="mensaje-icono-estado">{{ mensajeIcono }}</span>
          <p class="instruccion">{{ mensajeEstado }}</p>
        </div>

        <button @click="intentarMarcacion" :disabled="detectando" class="btn-capturar">
          📸 Verificar rostro
        </button>

        <div v-if="errorCamara" class="error-box">
          <span class="error-icono">⚠️</span> {{ errorCamara }}
        </div>
      </div>

      <!-- PASO: RESULTADO -->
      <div v-if="paso === 'resultado'" class="resultado-container">
        <div :class="['resultado-card', resultado.exito ? 'resultado-exito' : resultado.info ? 'resultado-info' : 'resultado-error']">

          <!-- Icono grande con emoji en lugar de img -->
          <div class="resultado-emoji">
            {{ resultado.exito ? '✅' : resultado.info ? 'ℹ️' : '❌' }}
          </div>

          <h3>{{ resultado.mensaje }}</h3>

          <div v-if="resultado.tipo || resultado.estado || resultado.hora" class="resultado-detalles">
            <div v-if="resultado.tipo" class="detalle-fila">
              <span class="detalle-label">Tipo</span>
              <span class="detalle-valor">{{ resultado.tipo }}</span>
            </div>
            <div v-if="resultado.estado" class="detalle-fila">
              <span class="detalle-label">Estado</span>
              <span class="detalle-valor" :class="resultado.estado === 'PUNTUAL' ? 'texto-verde' : 'texto-amarillo'">
                {{ resultado.estado }}
              </span>
            </div>
            <div v-if="resultado.hora" class="detalle-fila">
              <span class="detalle-label">Hora</span>
              <span class="detalle-valor">{{ resultado.hora }}</span>
            </div>
          </div>

          <div v-if="resultado.va_a_asistencia !== undefined" class="asistencia-badge"
               :class="resultado.va_a_asistencia ? 'badge-cuenta' : 'badge-no-cuenta'">
            {{ resultado.va_a_asistencia ? '✓ Registrada en asistencia' : 'ℹ Guardada solo en historial' }}
          </div>

          <div v-if="resultado.ubicacion && resultado.exito" class="ubicacion-resultado">
            <span>📍</span>
            <span>
              {{ resultado.ubicacion.ciudad || 'Red local' }}
              <span v-if="resultado.ubicacion.pais">, {{ resultado.ubicacion.pais }}</span>
            </span>
          </div>
        </div>

        <div class="resultado-botones">
          <button @click="$router.push('/trabajador/panel')" class="btn-si">Ir al panel</button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter }          from 'vue-router'
import { useThemeStore }      from '@/stores/theme'
import { useAuthStore }       from '@/stores/auth'
import { useFecha }           from '@/composables/useFecha'
import { useGeolocalizacion } from '@/composables/useGeolocalizacion'
import AppHeader              from '@/components/layout/AppHeader.vue'
import GeoStatus              from '@/components/marcaciones/GeoStatus.vue'
import api from '@/services/api'

const router = useRouter()
const theme  = useThemeStore()
const auth   = useAuthStore()
const { fechaHoraActual: fechaHora }                            = useFecha()
const { geoLatitud, geoLongitud, geoTexto, geoClase,
        pedirGeolocalizacion }                                  = useGeolocalizacion()

const videoRef         = ref(null)
const canvasRef        = ref(null)
const detectando       = ref(false)
const resultado        = ref(null)
const errorCamara      = ref('')
const mensajeEstado    = ref('Centre su rostro dentro del óvalo y presione el botón')
const estadoTipo       = ref('neutro') // 'neutro' | 'error' | 'advertencia' | 'ok'
const paso             = ref('camara')
const tipoMarcacion    = ref('ENTRADA')
const intentosRestantes = ref(null)

let stream = null

// ─── COMPUTED ──────────────────────────────────────────────────────────────
const estadoClase = computed(() => ({
  'estado-neutro':      estadoTipo.value === 'neutro',
  'estado-error':       estadoTipo.value === 'error',
  'estado-advertencia': estadoTipo.value === 'advertencia',
  'estado-ok':          estadoTipo.value === 'ok',
}))

const mensajeIcono = computed(() => {
  if (estadoTipo.value === 'error')       return '✗'
  if (estadoTipo.value === 'advertencia') return '!'
  if (estadoTipo.value === 'ok')          return '✓'
  return '○'
})

// ─── LIFECYCLE ─────────────────────────────────────────────────────────────
onMounted(async () => {
  pedirGeolocalizacion()
  await verificarTipoMarcacion()
})

onUnmounted(() => detenerCamara())

// ─── VERIFICAR TIPO ─────────────────────────────────────────────────────────
async function verificarTipoMarcacion() {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const { data: marcaciones } = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    const hoy = new Date().toLocaleDateString('es-PE')

    const hoyValidas = marcaciones.filter(m =>
      new Date(m.fecha).toLocaleDateString('es-PE') === hoy && m.va_a_asistencia === true
    )
    const entradaHoy = hoyValidas.find(m => m.tipo === 'ENTRADA_VALIDA' || m.tipo === 'ENTRADA')
    const salidaHoy  = hoyValidas.find(m => m.tipo === 'SALIDA_VALIDA'  || m.tipo === 'SALIDA')

    if (entradaHoy && salidaHoy) {
      paso.value = 'resultado'
      resultado.value = { exito: false, info: true, mensaje: 'Ya registró su asistencia de entrada y salida de hoy.', va_a_asistencia: true }
      return
    }

    const { data: perfil } = await api.get('/api/auth/perfil/')
    if (perfil.bloqueado) {
      paso.value = 'resultado'
      resultado.value = { exito: false, bloqueado: true, mensaje: 'Su cuenta está bloqueada. Contacte al administrador.' }
      return
    }

    tipoMarcacion.value = entradaHoy ? 'SALIDA' : 'ENTRADA'
    // Ir directo a cámara, sin confirmación
    paso.value = 'camara'
    await iniciarCamara()
  } catch {
    tipoMarcacion.value = 'ENTRADA'
    paso.value = 'camara'
    await iniciarCamara()
  }
}

// ─── CÁMARA ─────────────────────────────────────────────────────────────────
async function iniciarCamara() {
  errorCamara.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
    })
    videoRef.value.srcObject = stream
  } catch {
    errorCamara.value = 'No se pudo acceder a la cámara. Verifique los permisos.'
  }
}

function detenerCamara() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

// ─── CAPTURA OPTIMIZADA ─────────────────────────────────────────────────────
function capturarImagenOptimizada() {
  const canvas = canvasRef.value
  const video  = videoRef.value
  canvas.width  = 320
  canvas.height = 240
  canvas.getContext('2d').drawImage(video, 0, 0, 320, 240)
  return canvas.toDataURL('image/jpeg', 0.85)
}

// ─── MARCACION ──────────────────────────────────────────────────────────────
async function intentarMarcacion() {
  if (detectando.value) return
  detectando.value = true
  estadoTipo.value = 'neutro'
  mensajeEstado.value = 'Verificando identidad...'

  try {
    const payload = {
      trabajador_id: auth.usuario?.trabajador_id,
      imagen:        capturarImagenOptimizada(),
      dispositivo:   navigator.userAgent.includes('Mobile') ? 'Móvil' : 'PC Oficina',
    }
    if (geoLatitud.value  !== null) payload.latitud  = geoLatitud.value
    if (geoLongitud.value !== null) payload.longitud = geoLongitud.value

    const { data } = await api.post('/api/reconocimiento/verificar/', payload)

    detenerCamara()

    const marcacion    = data.marcacion
    const vaAsistencia = data.va_a_asistencia ?? marcacion?.va_a_asistencia ?? false

    resultado.value = {
      exito:  true,
      info:   !vaAsistencia,
      mensaje: data.mensaje || 'Marcación registrada',
      tipo:    marcacion?.tipo === 'ENTRADA_VALIDA' ? 'ENTRADA'
             : marcacion?.tipo === 'SALIDA_VALIDA'  ? 'SALIDA'
             : marcacion?.tipo,
      estado:          marcacion?.estado,
      hora:            marcacion?.fecha
                       ? new Date(marcacion.fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
                       : null,
      va_a_asistencia: vaAsistencia,
      ubicacion: data.ubicacion || {},
    }
    paso.value = 'resultado'

  } catch (e) {
    detectando.value = false

    const msg    = e.response?.data?.error || ''
    const status = e.response?.status
    const msgL   = msg.toLowerCase()

    if (!e.response) {
      return setMensajeError('Sin conexión con el servidor. Verifique su red e intente de nuevo.')
    }

    if (msgL.includes('más de un rostro') || msgL.includes('mas de un rostro')) {
      return setMensajeError('Se detectaron varias personas. Asegúrese de estar solo frente a la cámara.')
    }

    if (msgL.includes('no se detectó') || msgL.includes('no se pudo detectar') || msgL.includes('calidad')) {
      return setMensajeError('No se detectó rostro. Acérquese, mejore la iluminación y presione de nuevo.')
    }

    if (msgL.includes('no tiene embedding') || msgL.includes('embedding registrado')) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'Su rostro aún no ha sido registrado en el sistema. Comuníquese con el administrador.' }
      return
    }

    if (status === 403 && (msgL.includes('ip') || msgL.includes('red'))) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'No puede marcar desde esta red. Conéctese a la red autorizada de la Municipalidad.' }
      return
    }

    if (status === 403) {
      detenerCamara()
      paso.value = 'resultado'
      resultado.value = { exito: false, bloqueado: true, mensaje: msgL.includes('bloqueado') ? 'Usuario bloqueado por intentos fallidos. Contacte al administrador.' : msg }
      return
    }

    if (status === 401 || msgL.includes('no coincide')) {
      const match     = msg.match(/Intentos restantes:\s*(\d+)/i)
      const restantes = match ? parseInt(match[1]) : null

      if (restantes !== null) intentosRestantes.value = restantes

      if (restantes === 0 || msgL.includes('bloqueado')) {
        detenerCamara()
        paso.value = 'resultado'
        resultado.value = { exito: false, bloqueado: true, mensaje: 'Usuario bloqueado por demasiados intentos fallidos. Contacte al administrador.' }
        return
      }

      // Mensajes escalonados por urgencia
      if (restantes === 1) {
        return setMensajeError('Rostro no reconocido. Intente de nuevo en buenas condiciones de luz.', 'error')
      } else if (restantes === 2) {
        return setMensajeError('Rostro no reconocido. Acérquese más y mire de frente.', 'advertencia')
      } else {
        return setMensajeError('Rostro no reconocido. Reposiciónese frente a la cámara y vuelva a intentar.', 'neutro')
      }
    }

    if (status === 500) {
      return setMensajeError('Error en el servidor. Espere un momento e intente de nuevo.')
    }

    setMensajeError(msg || 'Error al procesar. Intente de nuevo.')
  }
}

// ─── HELPERS ────────────────────────────────────────────────────────────────
function setMensajeError(msg, tipo = 'error') {
  mensajeEstado.value = msg
  estadoTipo.value    = tipo
}

function reiniciar() {
  resultado.value         = null
  errorCamara.value       = ''
  mensajeEstado.value     = 'Centre su rostro dentro del óvalo y presione el botón'
  estadoTipo.value        = 'neutro'
  intentosRestantes.value = null
  verificarTipoMarcacion()
}

function volver() {
  detenerCamara()
  router.push('/trabajador/panel')
}
</script>

<style scoped>
.panel {
  --bg-main: #141416cc; --bg-card: #141416; --bg-soft: rgba(255,255,255,0.08);
  --text-main: #fcfcfd; --text-soft: rgba(255,255,255,0.6);
  --border-color: #232327; --accent: #18c440;
  min-height: 100vh; display: flex; flex-direction: column;
  background-color: var(--bg-main); color: var(--text-main);
}
.panel.light {
  --bg-main: #f8fafc; --bg-card: #ffffff; --bg-soft: #f1f5f9;
  --text-main: #0f172a; --text-soft: #64748b;
  --border-color: #e2e8f0; --accent: #2563eb;
}

/* CONTENT */
.content {
  position: relative; z-index: 10; flex: 1; padding: 28px 32px 24px;
  display: flex; flex-direction: column; gap: 24px;
  background-color: var(--bg-main); color: var(--text-main);
}

/* TÍTULO */
.titulo-seccion { display: flex; align-items: center; gap: 16px; }
.btn-volver {
  background: var(--bg-soft); border: 1px solid var(--border-color);
  color: var(--text-main); font-size: 0.9rem; font-weight: 600;
  padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease;
}
.btn-volver:hover { border-color: var(--accent); color: var(--accent); }
h2 { font-size: 1.3rem; font-weight: 700; color: var(--text-main); margin: 0; }

/* ALERTAS DE INTENTOS (solo ≤2) */
.alerta-intentos {
  display: flex; align-items: center; gap: 10px;
  width: 100%; max-width: 420px;
  padding: 12px 16px; border-radius: 10px;
  font-size: 0.88rem; font-weight: 600; line-height: 1.4;
  animation: pulso 1.8s ease-in-out infinite;
}
.alerta-advertencia {
  background: rgba(234, 179, 8, 0.12);
  border: 1.5px solid rgba(234, 179, 8, 0.5);
  color: #eab308;
}
.alerta-critica {
  background: rgba(239, 68, 68, 0.12);
  border: 1.5px solid rgba(239, 68, 68, 0.6);
  color: #ef4444;
}
.panel.light .alerta-advertencia { background: #fef9c3; color: #92400e; border-color: #fcd34d; }
.panel.light .alerta-critica     { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }
.alerta-icono { font-size: 1.1rem; flex-shrink: 0; }
.alerta-texto { flex: 1; }
@keyframes pulso {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.75; }
}

/* CÁMARA */
.camara-container { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.camara-wrapper {
  position: relative; width: 100%; max-width: 420px;
  border-radius: 14px; overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4); border: 1px solid var(--border-color); background: #000;
}
.video { width: 100%; display: block; aspect-ratio: 4/3; transform: scaleX(-1); object-fit: cover; }


.guia-rostro { position: absolute; inset: 0; pointer-events: none; display: flex; align-items: center; justify-content: center; }
.guia-svg { width: 90%; height: 90%; opacity: 0.9; }

/* MENSAJE DE ESTADO CON WRAPPER */
.mensaje-estado-wrapper {
  display: flex; align-items: flex-start; gap: 10px;
  width: 100%; max-width: 420px;
  padding: 12px 16px; border-radius: 10px;
  border: 1.5px solid transparent;
  transition: all 0.25s ease;
}
.mensaje-icono-estado {
  font-size: 1.1rem; font-weight: 800; line-height: 1.4;
  flex-shrink: 0; width: 20px; text-align: center;
}
.instruccion {
  font-size: 0.92rem; line-height: 1.5; margin: 0;
  transition: color 0.2s;
}

/* Variantes del mensaje */
.estado-neutro {
  background: var(--bg-soft);
  border-color: var(--border-color);
  color: var(--text-soft);
}
.estado-neutro .mensajeIcono { color: var(--text-soft); }

.estado-error {
  background: rgba(239, 68, 68, 0.10);
  border-color: rgba(239, 68, 68, 0.4);
  color: #ef4444;
}
.estado-error .instruccion { color: #ef4444; font-weight: 600; font-size: 0.95rem; }
.estado-error .mensaje-icono-estado { color: #ef4444; }

.estado-advertencia {
  background: rgba(234, 179, 8, 0.10);
  border-color: rgba(234, 179, 8, 0.4);
  color: #d97706;
}
.estado-advertencia .instruccion { color: #d97706; font-weight: 600; }
.estado-advertencia .mensaje-icono-estado { color: #d97706; }

.estado-ok {
  background: rgba(24, 196, 64, 0.10);
  border-color: rgba(24, 196, 64, 0.4);
  color: #18c440;
}
.estado-ok .instruccion { color: #18c440; font-weight: 600; }
.estado-ok .mensaje-icono-estado { color: #18c440; }

.panel.light .estado-neutro    { background: #f1f5f9; border-color: #e2e8f0; color: #64748b; }
.panel.light .estado-error     { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }
.panel.light .estado-advertencia { background: #fef9c3; border-color: #fcd34d; color: #92400e; }
.panel.light .estado-ok        { background: #dcfce7; border-color: #bbf7d0; color: #166534; }

/* BOTÓN CAPTURAR */
.btn-capturar {
  padding: 14px; background: var(--accent); color: white; border: none;
  border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease; width: 100%; max-width: 420px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.btn-capturar:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.btn-capturar:disabled { opacity: 0.5; cursor: not-allowed; background: #6b7280; }

.error-box {
  display: flex; align-items: center; gap: 8px;
  background: rgba(239,68,68,0.1); color: #ef4444;
  border: 1px solid rgba(239,68,68,0.3);
  padding: 12px 16px; border-radius: 10px; text-align: left;
  width: 100%; max-width: 420px; font-size: 0.9rem;
}
.panel.light .error-box { background: #fef2f2; color: #dc2626; border-color: #fecaca; }
.error-icono { font-size: 1rem; flex-shrink: 0; }

/* RESULTADO */
.resultado-container { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.resultado-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 16px; padding: 40px 48px; text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2); width: 100%; max-width: 420px;
}
.resultado-exito { border-top: 4px solid #18c440; }
.resultado-info  { border-top: 4px solid #f59e0b; }
.resultado-error { border-top: 4px solid #ef4444; }

.resultado-emoji { font-size: 3.5rem; margin-bottom: 16px; line-height: 1; }
.resultado-card h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 16px; }

/* Tabla de detalles del resultado */
.resultado-detalles {
  background: var(--bg-soft); border: 1px solid var(--border-color);
  border-radius: 10px; overflow: hidden; margin-bottom: 14px;
}
.detalle-fila {
  display: flex; justify-content: space-between; align-items: center;
  padding: 9px 14px; font-size: 0.88rem; border-bottom: 1px solid var(--border-color);
}
.detalle-fila:last-child { border-bottom: none; }
.detalle-label { color: var(--text-soft); }
.detalle-valor { font-weight: 600; color: var(--text-main); }
.texto-verde    { color: #18c440 !important; }
.texto-amarillo { color: #d97706 !important; }

.asistencia-badge {
  display: inline-block; margin: 0 auto 0;
  padding: 5px 16px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;
}
.badge-cuenta {
  background: rgba(24, 196, 64, 0.15); color: #18c440; border: 1px solid rgba(24, 196, 64, 0.3);
}
.badge-no-cuenta {
  background: rgba(251, 191, 36, 0.15); color: #65fd00; border: 1px solid rgba(251, 191, 36, 0.3);
}
.panel.light .badge-cuenta    { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.panel.light .badge-no-cuenta { background: #fef9c3; color: #854d0e; border-color: #fde68a; }

.ubicacion-resultado {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 14px;
  padding: 6px 14px; background: rgba(24,196,64,0.1);
  border: 1px solid rgba(24,196,64,0.25); border-radius: 20px; font-size: 0.82rem; color: #18c440;
}
.panel.light .ubicacion-resultado { background: #f0fdf4; color: #166534; border-color: #bbf7d0; }

/* BOTONES */
.btn-si {
  padding: 12px 32px; background: var(--accent); color: white; border: none;
  border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.2s ease;
}
.btn-si:hover { opacity: 0.88; transform: translateY(-1px); }
.btn-no {
  padding: 12px 32px; background: var(--bg-soft); color: var(--text-soft);
  border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.2s ease;
}
.btn-no:hover { border-color: var(--text-soft); color: var(--text-main); }
.resultado-botones { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* RESPONSIVE */
@media (max-width: 768px) {
  .content { padding: 16px; gap: 16px; }
  h2 { font-size: 1.1rem; }
  .btn-capturar { padding: 14px; font-size: 0.95rem; }
  .resultado-card { padding: 28px 20px; }
  .resultado-botones { flex-direction: column; width: 100%; max-width: 420px; }
  .resultado-botones .btn-si, .resultado-botones .btn-no { width: 100%; }
}
</style>