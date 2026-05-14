<template>
  <div class="panel" :class="{ light: !theme.oscuro }">
    <div class="bg-overlay"></div>

    <!-- HEADER -->
    <AppHeader />

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
                    <img :src="clima.icono" class="clima-icon" />
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
import imagenHistorial      from '@/assets/lista-historial.webp'
import imagenAsistencia     from '@/assets/asistencia.webp'
import relojArena           from '@/assets/imagen/reloj-de-arena.png'
import iconoAlerta          from '@/assets/imagen/mano-reloj.png'
import iconoCheck           from '@/assets/icons/icon-check.svg'

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore }  from '@/stores/auth'
import { useClima }      from '@/composables/useClima'
import { useCalendario } from '@/composables/useCalendario'
import AppHeader from '@/components/layout/AppHeader.vue'
import { FRASES } from '@/assets/data/frases'
import { CURIOSIDADES } from '@/assets/data/curiosidades'
import api from '@/services/api'

const auth  = useAuthStore()
const theme = useThemeStore()
// handleLogout no se usa en el template de PanelView directamente —
// lo maneja AppHeader internamente

const { clima, cargarClima }                              = useClima()
const { nombreMes, anioCalendario, diasCalendario,
        cargarFeriados, mesAnterior, mesSiguiente }       = useCalendario()

// ── Saludo ───────────────────────────────────────────────────
const saludo = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 18) return 'Buenas tardes'
  return 'Buenas noches'
})
const fechaHoy = computed(() =>
  new Date().toLocaleDateString('es-PE', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
)

// para la frase aleatoria
const frase = ref('')
const fraseAutor = ref('')

const CONTENIDO = [...FRASES, ...CURIOSIDADES]

function cargarFrase() {
  const f = CONTENIDO[Math.floor(Math.random() * CONTENIDO.length)]

  frase.value = f.t
  fraseAutor.value = f.a
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
</script>

<style scoped src="./style.css"></style>