<template>
  <div class="marcar">

    <header class="header">
      <div class="header-left">
        <img src="/logo-2.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-usuario">👤 {{ auth.usuario?.nombre_completo }}</span>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="main">
      <div class="titulo-seccion">
        <button @click="volver" class="btn-volver">← Volver</button>
        <h2>Marcar Asistencia</h2>
      </div>

      <!-- PASO 1: CONFIRMACIÓN -->
      <div v-if="paso === 'confirmar'" class="confirmacion-container">
        <div class="confirmacion-card">
          <div class="confirmacion-icono">{{ tipoMarcacion === 'ENTRADA' ? '🕐' : '🕔' }}</div>
          <h3>{{ tipoMarcacion === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida' }}</h3>
          <p>{{ fechaHora }}</p>
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
          <div class="ovalo-container">
            <svg class="ovalo-svg" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <mask id="mask">
                  <rect width="300" height="400" fill="white"/>
                  <ellipse cx="150" cy="190" rx="100" ry="130" fill="black"/>
                </mask>
              </defs>
              <rect width="300" height="400" fill="rgba(0,0,0,0.45)" mask="url(#mask)"/>
              <ellipse
                cx="150" cy="190" rx="100" ry="130"
                fill="none"
                :stroke="detectando ? '#22c55e' : 'rgba(255,255,255,0.8)'"
                stroke-width="3"
                :class="{ pulsando: detectando }"
              />
            </svg>
          </div>
          <canvas ref="canvasRef" style="display:none"></canvas>
        </div>

        <div class="estado-deteccion">
          <div class="punto" :class="{ procesando: detectando }"></div>
          <p>{{ mensajeEstado }}</p>
        </div>

        <div v-if="errorCamara" class="error">{{ errorCamara }}</div>
      </div>

      <!-- PASO 3: RESULTADO -->
      <div v-if="paso === 'resultado'" class="resultado-container">
        <div :class="['resultado', resultado.exito ? 'resultado-exito' : 'resultado-error']">
          <div class="resultado-icono">{{ resultado.exito ? '✅' : '❌' }}</div>
          <h3>{{ resultado.mensaje }}</h3>
          <p v-if="resultado.tipo">
            Tipo: <strong>{{ resultado.tipo }}</strong>
          </p>
          <p v-if="resultado.estado">
            Estado:
            <strong :class="resultado.estado === 'PUNTUAL' ? 'texto-verde' : 'texto-amarillo'">
              {{ resultado.estado }}
            </strong>
          </p>
          <p v-if="resultado.similitud">
            Similitud: <strong>{{ (resultado.similitud * 100).toFixed(1) }}%</strong>
          </p>
          <p v-if="resultado.hora">
            Hora: <strong>{{ resultado.hora }}</strong>
          </p>
        </div>
        <button v-if="resultado.exito" @click="$router.push('/trabajador/panel')" class="btn-panel">
          Ir al panel
        </button>
        <button v-if="!resultado.exito && !resultado.mensaje.includes('entrada y salida')" @click="reiniciar" class="btn-reiniciar">
          Intentar de nuevo
        </button>
        <button v-if="!resultado.exito" @click="$router.push('/trabajador/panel')" class="btn-panel">
          Ir al panel
        </button>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

const videoRef = ref(null)
const canvasRef = ref(null)
const detectando = ref(false)
const resultado = ref(null)
const errorCamara = ref('')
const mensajeEstado = ref('Posicione su rostro dentro del óvalo...')
const paso = ref('confirmar')
const tipoMarcacion = ref('ENTRADA')

let stream = null
let intervalo = null
let intentosFallidos = 0
const MAX_INTENTOS = 5

const fechaHora = computed(() => {
  return new Date().toLocaleString('es-PE', {
    weekday: 'long', year: 'numeric',
    month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
})

onMounted(async () => {
  await verificarTipoMarcacion()
})

onUnmounted(() => {
  detenerTodo()
})

async function verificarTipoMarcacion() {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const response = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    const marcaciones = response.data

    const hoy = new Date().toLocaleDateString('es-PE')
    const hoyMarcaciones = marcaciones.filter(m => {
      return new Date(m.fecha).toLocaleDateString('es-PE') === hoy
    })

    const entradaHoy = hoyMarcaciones.find(m => m.tipo === 'ENTRADA')
    const salidaHoy = hoyMarcaciones.find(m => m.tipo === 'SALIDA')

    if (entradaHoy && salidaHoy) {
      paso.value = 'resultado'
      resultado.value = {
        exito: false,
        mensaje: '✅ Ya registró su asistencia de entrada y salida de hoy'
      }
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
      video: {
        facingMode: 'user',
        width: { ideal: 480 },
        height: { ideal: 640 }
      }
    })
    videoRef.value.srcObject = stream
    setTimeout(() => iniciarDeteccionAutomatica(), 2000)
  } catch (e) {
    errorCamara.value = 'No se pudo acceder a la cámara. Verifique los permisos.'
  }
}

function iniciarDeteccionAutomatica() {
  intervalo = setInterval(async () => {
    if (!detectando.value && paso.value === 'camara') {
      await intentarMarcacion()
    }
  }, 3000)
}

async function intentarMarcacion() {
  detectando.value = true
  mensajeEstado.value = 'Detectando rostro...'

  try {
    const canvas = canvasRef.value
    const video = videoRef.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    const imagenBase64 = canvas.toDataURL('image/jpeg', 0.95)

    const response = await api.post('/api/reconocimiento/verificar/', {
      trabajador_id: auth.usuario?.trabajador_id,
      imagen: imagenBase64,
      dispositivo: navigator.userAgent.includes('Mobile') ? 'Móvil' : 'PC Oficina'
    })

    detenerTodo()
    const marcacion = response.data.marcacion
    resultado.value = {
      exito: true,
      mensaje: `${marcacion.tipo === 'ENTRADA' ? 'Entrada' : 'Salida'} registrada correctamente`,
      tipo: marcacion.tipo,
      estado: marcacion.estado,
      similitud: response.data.similitud,
      hora: new Date(marcacion.fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit'
      })
    }
    paso.value = 'resultado'

  } catch (e) {
    const errorMsg = e.response?.data?.error || ''
    const status = e.response?.status

    // No hay rostro o calidad baja — no contar intento
    if (!e.response || errorMsg.includes('no se detectó') ||
        errorMsg.includes('calidad') || errorMsg.includes('No se detectó')) {
      mensajeEstado.value = 'Posicione su rostro dentro del óvalo...'
      detectando.value = false
      return
    }

    // Ya marcó hoy
    if (errorMsg.includes('entrada y salida')) {
      detenerTodo()
      resultado.value = {
        exito: false,
        mensaje: '✅ Ya registró su asistencia de entrada y salida de hoy'
      }
      paso.value = 'resultado'
      return
    }

    // Usuario bloqueado por el backend
    if (status === 403) {
      detenerTodo()
      resultado.value = { exito: false, mensaje: errorMsg }
      paso.value = 'resultado'
      return
    }

    // Rostro no coincide — mostrar advertencias progresivas
    if (errorMsg.includes('no coincide') || status === 401) {
      intentosFallidos++

      if (intentosFallidos <= 2) {
        mensajeEstado.value = 'Posicione su rostro dentro del óvalo...'
      } else if (intentosFallidos === 3) {
        mensajeEstado.value = '⚠️ Acérquese más a la cámara y mejore la iluminación'
      } else if (intentosFallidos === 4) {
        mensajeEstado.value = '⚠️ Mire de frente y asegúrese de tener buena iluminación'
      } else if (intentosFallidos === 5) {
        mensajeEstado.value = '🔴 Último intento — si falla contacte al administrador'
      } else {
        detenerTodo()
        resultado.value = {
          exito: false,
          mensaje: 'No se pudo verificar su identidad. Contacte al administrador para desbloquear su cuenta.'
        }
        paso.value = 'resultado'
      }

      detectando.value = false
      return
    }

    // Cualquier otro error
    intentosFallidos++
    mensajeEstado.value = 'Posicione su rostro dentro del óvalo...'
    detectando.value = false
  }
}

function detenerTodo() {
  if (intervalo) { clearInterval(intervalo); intervalo = null }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

function reiniciar() {
  resultado.value = null
  errorCamara.value = ''
  intentosFallidos = 0
  mensajeEstado.value = 'Posicione su rostro dentro del óvalo...'
  verificarTipoMarcacion()
}

function volver() {
  detenerTodo()
  router.push('/trabajador/panel')
}

async function handleLogout() {
  detenerTodo()
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.marcar {
  min-height: 100vh;
  background-color: #f0f4f8;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #1a3a6b;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left { display: flex; align-items: center; gap: 10px; }
.logo { width: 40px; height: 40px; object-fit: contain; }
.sistema-nombre { color: white; font-weight: bold; font-size: 1rem; }
.header-right { display: flex; align-items: center; gap: 16px; }
.nombre-usuario { color: white; font-size: 0.9rem; }

.btn-logout {
  background: transparent;
  border: 1px solid white;
  color: white;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-logout:hover { background: white; color: #1a3a6b; }

.main {
  flex: 1;
  padding: 32px 24px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.titulo-seccion {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-volver {
  background: none;
  border: none;
  color: #1a3a6b;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
}

h2 { font-size: 1.3rem; color: #1a3a6b; }

/* CONFIRMACIÓN */
.confirmacion-container {
  display: flex;
  justify-content: center;
}

.confirmacion-card {
  background: white;
  border-radius: 16px;
  padding: 40px 48px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 100%;
}

.confirmacion-icono { font-size: 3.5rem; margin-bottom: 12px; }

.confirmacion-card h3 {
  font-size: 1.3rem;
  color: #1a3a6b;
  margin-bottom: 6px;
}

.confirmacion-card p {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.confirmacion-pregunta {
  font-size: 1rem !important;
  color: #333 !important;
  margin: 20px 0 24px !important;
}

.confirmacion-botones {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-no {
  padding: 12px 32px;
  background: white;
  color: #666;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-no:hover { border-color: #999; color: #333; }

.btn-si {
  padding: 12px 32px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-si:hover { background: #142d54; }

/* CÁMARA */
.camara-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.camara-wrapper {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 320px;
}

.video {
  width: 100%;
  display: block;
  aspect-ratio: 3/4;
  object-fit: cover;
}

.ovalo-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.ovalo-svg {
  width: 100%;
  height: 100%;
}

.pulsando {
  animation: pulsar 1s infinite;
}

@keyframes pulsar {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.estado-deteccion {
  display: flex;
  align-items: center;
  gap: 10px;
}

.punto {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
}

.punto.procesando {
  background: #f59e0b;
  animation: parpadear 0.8s infinite;
}

@keyframes parpadear {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

.estado-deteccion p { font-size: 0.9rem; color: #555; }

/* RESULTADO */
.resultado-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.resultado {
  background: white;
  border-radius: 16px;
  padding: 36px 48px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.resultado-exito { border-top: 5px solid #22c55e; }
.resultado-error { border-top: 5px solid #ef4444; }

.resultado-icono { font-size: 3.5rem; margin-bottom: 16px; }
.resultado h3 { font-size: 1.1rem; color: #333; margin-bottom: 12px; }
.resultado p { color: #555; font-size: 0.9rem; margin: 6px 0; }

.texto-verde { color: #16a34a; }
.texto-amarillo { color: #ca8a04; }

.btn-reiniciar {
  padding: 10px 28px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-panel {
  padding: 10px 28px;
  background: white;
  color: #1a3a6b;
  border: 2px solid #1a3a6b;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  width: 100%;
  max-width: 320px;
}
</style>