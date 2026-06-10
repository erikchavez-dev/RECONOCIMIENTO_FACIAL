<template>
  <div class="panel" :class="{ light: !theme.oscuro }">
 
    <AppHeader :antes-de-logout="detenerCamara" />
 
    <main class="content">
      <div class="titulo-seccion">
        <button @click="volver" class="btn-volver">← Volver</button>
        <h2>Marcar Asistencia</h2>
      </div>
 
      <!-- PASO: CÁMARA -->
      <div v-if="paso === 'camara'" class="camara-container">
 
        <div v-if="intentosRestantes !== null && intentosRestantes <= 2" class="alerta-intentos"
             :class="intentosRestantes === 1 ? 'alerta-critica' : 'alerta-advertencia'">
          <span class="alerta-icono">{{ intentosRestantes === 1 ? '' : '' }}</span>
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
              <ellipse cx="160" cy="160" rx="100" ry="120"
                fill="none" stroke="rgba(3,221,83,0.8)"
                stroke-width="2.5" stroke-dasharray="8 4" />
            </svg>
          </div>
          <canvas ref="canvasRef" style="display:none"></canvas>
        </div>
 
        <div class="mensaje-estado-wrapper" :class="estadoClase">
          <p class="instruccion">{{ mensajeEstado }}</p>
        </div>
 
        <button @click="intentarMarcacion" :disabled="detectando" class="btn-capturar">
          Verificar rostro
        </button>
 
        <div v-if="errorCamara" class="error-box">
          <span class="error-icono"></span> {{ errorCamara }}
        </div>
      </div>
 
      <!-- PASO: RESULTADO — se muestra siempre (éxito o error) -->
      <div v-if="paso === 'resultado' && resultado" class="resultado-container">
        <div :class="['resultado-card',
          resultado.exito ? 'resultado-exito' :
          resultado.info  ? 'resultado-info'  : 'resultado-error']">
 
          <div class="resultado-emoji">
            {{ resultado.exito ? '' : resultado.info ? 'ℹ' : '' }}
          </div>
 
          <h3>{{ resultado.mensaje }}</h3>
 
          <div v-if="resultado.tipo || resultado.estado || resultado.hora" class="resultado-detalles">
            <div v-if="resultado.tipo" class="detalle-fila">
              <span class="detalle-label">Tipo</span>
              <span class="detalle-valor">{{ resultado.tipo }}</span>
            </div>
            <div v-if="resultado.estado" class="detalle-fila">
              <span class="detalle-label">Estado</span>
              <span class="detalle-valor"
                :class="resultado.estado === 'PUNTUAL' ? 'texto-verde' : 'texto-amarillo'">
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
            <span></span>
            <span>
              {{ resultado.ubicacion.ciudad || 'Red local' }}
              <span v-if="resultado.ubicacion.pais">, {{ resultado.ubicacion.pais }}</span>
            </span>
          </div>
        </div>
 
        <div class="resultado-botones">
          <button @click="$router.push('/trabajador/panel')" class="btn-si">Ir al panel</button>
          <button v-if="!resultado.exito && !resultado.info && !resultado.bloqueado"
            @click="reiniciar" class="btn-no">
            Intentar de nuevo
          </button>
        </div>
      </div>
    </main>
 
    <!-- OVERLAY — aparece 1.5s después del éxito, encima de la tarjeta -->
    <div v-if="mostrarOverlay" class="exito-overlay">
      <div class="exito-card" :class="{ 'exito-card-out': cardSaliendo }">
        <div class="exito-circle">
          <svg viewBox="0 0 120 120">
            <circle class="exito-bg"       cx="60" cy="60" r="50" />
            <circle class="exito-progress" cx="60" cy="60" r="50" />
            <path   class="exito-check"    d="M40 62 L54 76 L82 48" />
          </svg>
        </div>
        <h2 class="exito-titulo">Completado</h2>
        <p class="exito-subtexto">Preparando la siguiente pantalla...</p>
      </div>
    </div>
 
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
import api from '@/services/api'
 
const router = useRouter()
const theme  = useThemeStore()
const auth   = useAuthStore()
const { fechaHoraActual: fechaHora } = useFecha()
const { geoLatitud, geoLongitud, pedirGeolocalizacion } = useGeolocalizacion()
 
const videoRef          = ref(null)
const canvasRef         = ref(null)
const detectando        = ref(false)
const resultado         = ref(null)
const errorCamara       = ref('')
const mensajeEstado     = ref('Centre su rostro dentro del óvalo y presione el botón')
const estadoTipo        = ref('neutro')
const paso              = ref('camara')
const tipoMarcacion     = ref('ENTRADA')
const intentosRestantes = ref(null)
 
const mostrarOverlay = ref(false)
const cardSaliendo   = ref(false)
let   t1 = null, t2 = null, t3 = null
 
let stream = null
 
const estadoClase = computed(() => ({
  'estado-neutro':      estadoTipo.value === 'neutro',
  'estado-error':       estadoTipo.value === 'error',
  'estado-advertencia': estadoTipo.value === 'advertencia',
  'estado-ok':          estadoTipo.value === 'ok',
}))
 
onMounted(async () => {
  pedirGeolocalizacion()
  await verificarTipoMarcacion()
})
 
onUnmounted(() => { detenerCamara(); limpiarTimers() })
 
function limpiarTimers() {
  [t1, t2, t3].forEach(t => t && clearTimeout(t))
  t1 = t2 = t3 = null
}
 
// Flujo: overlay aparece inmediatamente → anima 3.2s → desvanece 0.7s → redirige
function lanzarOverlay() {
  mostrarOverlay.value = true
  cardSaliendo.value   = false
 
  t2 = setTimeout(() => {
    cardSaliendo.value = true
 
    t3 = setTimeout(() => {
      limpiarTimers()
      router.push('/trabajador/panel')
    }, 700)
  }, 2500)
}
 
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
    paso.value = 'camara'
    await iniciarCamara()
  } catch {
    tipoMarcacion.value = 'ENTRADA'
    paso.value = 'camara'
    await iniciarCamara()
  }
}
 
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
 
function capturarImagenOptimizada() {
  const canvas = canvasRef.value
  const video  = videoRef.value
  canvas.width  = 320
  canvas.height = 240
  canvas.getContext('2d').drawImage(video, 0, 0, 320, 240)
  return canvas.toDataURL('image/jpeg', 0.85)
}
 
async function intentarMarcacion() {
  if (detectando.value) return
  detectando.value    = true
  estadoTipo.value    = 'neutro'
  mensajeEstado.value = 'Verificando identidad...'
 
  try {
    const payload = {
      trabajador_id: auth.usuario?.trabajador_id,
      imagen:        capturarImagenOptimizada(),
      dispositivo:   navigator.userAgent.includes('Mobile') ? 'Móvil' : 'PC Oficina',
      navegador:     navigator.userAgent,
    }
    if (geoLatitud.value  !== null) payload.latitud  = geoLatitud.value
    if (geoLongitud.value !== null) payload.longitud = geoLongitud.value
 
    const { data } = await api.post('/api/reconocimiento/verificar/', payload)
    detenerCamara()
 
    const marcacion    = data.marcacion
    const vaAsistencia = data.va_a_asistencia ?? marcacion?.va_a_asistencia ?? false
 
    resultado.value = {
      exito:   true,
      mensaje: data.mensaje || 'Marcación registrada',
      tipo:    marcacion?.tipo === 'ENTRADA_VALIDA' ? 'ENTRADA'
             : marcacion?.tipo === 'SALIDA_VALIDA'  ? 'SALIDA'
             : marcacion?.tipo,
      estado:          marcacion?.estado,
      hora:            marcacion?.fecha
                       ? new Date(marcacion.fecha).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
                       : null,
      va_a_asistencia: vaAsistencia,
      ubicacion:       data.ubicacion || {},
    }
    paso.value = 'resultado'
    t1 = setTimeout(() => {
      lanzarOverlay()
    }, 1500)
 
  } catch (e) {
    detectando.value = false
    const msg        = e.response?.data?.error  || ''
    const codigo     = e.response?.data?.codigo || ''
    const httpStatus = e.response?.status
    const msgL       = msg.toLowerCase()
 
    if (!e.response)
      return setMensajeError('Sin conexión con el servidor. Verifique su red e intente de nuevo.')
 
    if (msgL.includes('más de un rostro') || msgL.includes('mas de un rostro'))
      return setMensajeError('Se detectaron varias personas. Asegúrese de estar solo frente a la cámara.')
 
    if (msgL.includes('no se detectó') || msgL.includes('no se pudo detectar') || msgL.includes('calidad'))
      return setMensajeError('No se detectó rostro. Acérquese, mejore la iluminación y presione de nuevo.')
 
    if (msgL.includes('no tiene embedding') || msgL.includes('embedding registrado')) {
      detenerCamara(); paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'Su rostro aún no ha sido registrado. Comuníquese con el administrador.' }
      return
    }
 
    if (codigo === 'GEOCERCA_RECHAZADO' || msgL.includes('fuera del área') || msgL.includes('geocerca')) {
      detenerCamara(); paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: msg || 'Marcación rechazada: no se encuentra dentro del área autorizada.' }
      return
    }
 
    if (httpStatus === 403 && (msgL.includes('ip') || msgL.includes('red'))) {
      detenerCamara(); paso.value = 'resultado'
      resultado.value = { exito: false, mensaje: 'No puede marcar desde esta red. Conéctese a la red autorizada.' }
      return
    }
 
    if (httpStatus === 403) {
      detenerCamara(); paso.value = 'resultado'
      resultado.value = {
        exito: false, bloqueado: msgL.includes('bloqueado'),
        mensaje: msgL.includes('bloqueado')
          ? 'Usuario bloqueado por intentos fallidos. Contacte al administrador.' : msg,
      }
      return
    }
 
    if (httpStatus === 401 || msgL.includes('no coincide')) {
      const match     = msg.match(/Intentos restantes:\s*(\d+)/i)
      const restantes = match ? parseInt(match[1]) : null
      if (restantes !== null) intentosRestantes.value = restantes
 
      if (restantes === 0 || msgL.includes('bloqueado')) {
        detenerCamara(); paso.value = 'resultado'
        resultado.value = { exito: false, bloqueado: true, mensaje: 'Usuario bloqueado. Contacte al administrador.' }
        return
      }
      if (restantes === 1)      return setMensajeError('Rostro no reconocido. Intente en buenas condiciones de luz.', 'error')
      else if (restantes === 2) return setMensajeError('Rostro no reconocido. Acérquese más y mire de frente.', 'advertencia')
      else                      return setMensajeError('Rostro no reconocido. Reposiciónese y vuelva a intentar.', 'neutro')
    }
 
    if (httpStatus === 500) return setMensajeError('Error en el servidor. Espere un momento e intente de nuevo.')
    setMensajeError(msg || 'Error al procesar. Intente de nuevo.')
  }
}
 
function setMensajeError(msg, tipo = 'error') {
  mensajeEstado.value = msg
  estadoTipo.value    = tipo
}
 
function reiniciar() {
  limpiarTimers()
  mostrarOverlay.value = false; cardSaliendo.value = false
  resultado.value = null; errorCamara.value = ''
  mensajeEstado.value = 'Centre su rostro dentro del óvalo y presione el botón'
  estadoTipo.value = 'neutro'; intentosRestantes.value = null
  verificarTipoMarcacion()
}
 
function volver() { detenerCamara(); limpiarTimers(); router.push('/trabajador/panel') }
</script>
 
<style scoped src="./style.css"></style>