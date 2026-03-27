<template>
  <div class="marcar">

    <header class="header">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-usuario"><img :src="iconoPerfil" class="icono-perfil" />{{ auth.usuario?.nombre_completo }}</span>
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
          <div class="confirmacion-icono">{{ tipoMarcacion === 'ENTRADA' ? '' : '' }}</div>
          <h3>{{ tipoMarcacion === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida' }}</h3>
          <p class="fecha-texto">{{ fechaHora }}</p>
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
          <!-- Guía de posición del rostro -->
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

        <div v-if="errorCamara" class="error">{{ errorCamara }}</div>
      </div>

      <!-- PASO 3: RESULTADO -->
      <div v-if="paso === 'resultado'" class="resultado-container">
        <div :class="['resultado', resultado.exito ? 'resultado-exito' : 'resultado-error']">
          <div class="resultado-icono">{{ resultado.exito ? '' : '' }}</div>
          <h3>{{ resultado.mensaje }}</h3>
          <p v-if="resultado.tipo">Tipo: <strong>{{ resultado.tipo }}</strong></p>
          <p v-if="resultado.estado">
            Estado:
            <strong :class="resultado.estado === 'PUNTUAL' ? 'texto-verde' : 'texto-amarillo'">
              {{ resultado.estado }}
            </strong>
          </p>
          <!-- <p v-if="resultado.similitud">
            Similitud: <strong>{{ (resultado.similitud * 100).toFixed(1) }}%</strong>
          </p> -->
          <p v-if="resultado.hora">Hora: <strong>{{ resultado.hora }}</strong></p>
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
import iconoPerfil from '@/assets/icon-perfil.svg'

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
const mensajeEstado = ref('Centre su rostro frente a la cámara y presione el botón')
const paso = ref('confirmar')
const tipoMarcacion = ref('ENTRADA')

let stream = null
// Sin MAX_INTENTOS local — el backend decide cuándo bloquear

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
  detenerCamara()
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
        mensaje: 'Ya registró su asistencia de entrada y salida de hoy'
      }
      return
    }
    const perfilResponse = await api.get('/api/auth/perfil/')
    if (perfilResponse.data.bloqueado) {
      paso.value = 'resultado'
      resultado.value = {
        exito: false,
        mensaje: 'Su cuenta está bloqueada por intentos fallidos. Contacte al administrador.'
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
      video: { facingMode: 'user', width: 640, height: 480 }
    })
    videoRef.value.srcObject = stream
  } catch (e) {
    errorCamara.value = 'No se pudo acceder a la cámara. Verifique los permisos.'
  }
}

function detenerCamara() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
}

async function intentarMarcacion() {
  if (detectando.value) return
  detectando.value = true
  mensajeEstado.value = 'Verificando...'

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

    detenerCamara()
    const marcacion = response.data.marcacion
    resultado.value = {
      exito: true,
      mensaje: `${marcacion.tipo === 'ENTRADA' ? 'Entrada' : 'Salida'} registrada correctamente`,
      tipo: marcacion.tipo,
      estado: marcacion.estado,
      hora: new Date(marcacion.fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit'
      })
    }
    paso.value = 'resultado'

  } catch (e) {
    const errorMsg = e.response?.data?.error || ''
    const httpStatus = e.response?.status

    // Sin rostro o calidad baja — no cuenta como intento
    if (!e.response || errorMsg.includes('no se detectó') ||
      errorMsg.includes('calidad') || errorMsg.includes('No se detectó')) {
      mensajeEstado.value = 'No se detectó rostro. Acérquese más, mejore la iluminación y presione de nuevo.'
      detectando.value = false
      return
    }

    // Ya marcó hoy
    if (errorMsg.includes('entrada y salida')) {
      detenerCamara()
      resultado.value = {
        exito: false,
        mensaje: 'Ya registró su asistencia de entrada y salida de hoy'
      }
      paso.value = 'resultado'
      return
    }

    // 403 — bloqueado por IP o por intentos (lo decide el backend)
    if (httpStatus === 403) {
      detenerCamara()
      resultado.value = {
        exito: false,
        mensaje: errorMsg.includes('IP')
          ? 'No puede marcar desde esta red. Conéctese a la red autorizada.'
          : 'Usuario bloqueado por intentos fallidos. Contacte al administrador.'
      }
      paso.value = 'resultado'
      return
    }

    // 401 — rostro no coincide, el backend indica cuántos intentos quedan
    if (errorMsg.includes('no coincide') || httpStatus === 401) {
      // Extraer intentos restantes del mensaje del backend
      const match = errorMsg.match(/Intentos restantes: (\d+)/)
      const restantes = match ? parseInt(match[1]) : null

      if (restantes === null) {
        mensajeEstado.value = 'Rostro no coincide. Posiciónese bien y presione de nuevo.'
      } else if (restantes >= 4) {
        mensajeEstado.value = 'Rostro no coincide. Posiciónese bien y presione de nuevo.'
      } else if (restantes === 3) {
        mensajeEstado.value = '⚠️ Acérquese más a la cámara y mejore la iluminación'
      } else if (restantes === 2) {
        mensajeEstado.value = '⚠️ Mire de frente con buena iluminación'
      } else if (restantes === 1) {
        mensajeEstado.value = '🔴 Último intento — si falla será bloqueado'
      } else {
        mensajeEstado.value = 'Rostro no coincide. Intente de nuevo.'
      }

      detectando.value = false
      return
    }

    mensajeEstado.value = 'Error al procesar. Intente de nuevo.'
    detectando.value = false
  }
}

function reiniciar() {
  resultado.value = null
  errorCamara.value = ''
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
.logo {
  width: 180px;
  height: 60px;
  object-fit: contain;
}

.marcar {
  min-height: 100vh;
  background-color: #f0f4f8;
  display: flex;
  flex-direction: column;
}

.icono-perfil {
  width: 20px;
  height: 20px;
  margin-right: 6px;
}


.header {
  background-color: #1a3a6b;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left { display: flex; align-items: center; gap: 10px; }

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
  padding: 24px;
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
  font-size: 1.02rem;
  cursor: pointer;
  font-weight: 600;
}

h2 { font-size: 1.3rem; color: #1a3a6b; }

/* CONFIRMACIÓN */
.confirmacion-container { display: flex; justify-content: center; }

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

.fecha-texto {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.confirmacion-pregunta {
  font-size: 1rem;
  color: #333;
  margin: 20px 0 24px;
}

.confirmacion-botones { display: flex; gap: 16px; justify-content: center; }

.btn-no {
  padding: 12px 32px;
  background: white;
  color: #666;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
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
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
  background: #000;
}

.video {
  width: 100%;
  display: block;
  aspect-ratio: 4/3;
  object-fit: cover;
}

.instruccion {
  font-size: 0.9rem;
  color: #555;
  text-align: center;
  max-width: 420px;
}

.btn-capturar {
  padding: 14px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
  max-width: 420px;
}

.btn-capturar:hover:not(:disabled) { background: #142d54; }
.btn-capturar:disabled { opacity: 0.7; cursor: not-allowed; }

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
  max-width: 420px;
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

.sistema-nombre {
  color: white;
  font-weight: bold;
  font-size: 1.4em;
}

</style>