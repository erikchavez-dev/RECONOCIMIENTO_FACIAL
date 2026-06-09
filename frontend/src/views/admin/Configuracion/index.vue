<!-- ConfiguracionView.vue -->
<template>
  <AdminLayout titulo="Configuración">

    <div v-if="cargando" class="cargando">Cargando configuración...</div>

    <div v-else class="config-container">

      <!-- HORARIOS DE ENTRADA (ADMIN + SUPERADMIN) -->
      <div class="seccion">
        <h3>Horarios de Entrada</h3>
        <div class="horario-info">
          <span class="horario-tag">Puntual</span> si llega antes de la hora fin entrada.
          <span class="horario-tag tardanza">Tardanza</span> si llega después pero dentro de la tolerancia.
          <span class="horario-tag fuera">Fuera</span> si supera la tolerancia.
        </div>
        <div class="form-grid">
          <div class="campo">
            <label>Hora inicio entrada</label>
            <div class="time-picker">
              <select v-model="horasEntrada.inicio_h" class="sel-hora">
                <option v-for="h in horas12" :key="h" :value="h">{{ h }}</option>
              </select>
              <span class="sep">:</span>
              <select v-model="horasEntrada.inicio_m" class="sel-min">
                <option v-for="m in minutos" :key="m" :value="m">{{ m }}</option>
              </select>
              <select v-model="horasEntrada.inicio_ampm" class="sel-ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
            <span class="hint-hora">24h: {{ form.hora_inicio_entrada }}</span>
          </div>
          <div class="campo">
            <label>Hora fin entrada (límite puntualidad)</label>
            <div class="time-picker" :class="{ 'time-picker-error': erroresHorario.fin_entrada }">
              <select v-model="horasEntrada.fin_h" class="sel-hora">
                <option v-for="h in horas12" :key="h" :value="h">{{ h }}</option>
              </select>
              <span class="sep">:</span>
              <select v-model="horasEntrada.fin_m" class="sel-min">
                <option v-for="m in minutos" :key="m" :value="m">{{ m }}</option>
              </select>
              <select v-model="horasEntrada.fin_ampm" class="sel-ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
            <span class="hint-hora">24h: {{ form.hora_fin_entrada }}</span>
            <span v-if="erroresHorario.fin_entrada" class="error-inline">⚠ {{ erroresHorario.fin_entrada }}</span>
          </div>
        </div>
        <div class="campo tolerancia-campo">
          <label>Tolerancia de tardanza (minutos)</label>
          <div class="tolerancia-row">
            <input v-model.number="form.tolerancia_minutos" type="number" min="0" max="120" step="5"
              class="input-tolerancia" />
            <span class="tolerancia-hint">min. Hasta las <strong>{{ limiteTolerancia }}</strong> se acepta como
              tardanza.</span>
          </div>
          <span class="hint">0 = sin tolerancia. Máx. 120 min.</span>
        </div>
      </div>

      <!-- HORARIOS DE SALIDA (ADMIN + SUPERADMIN) -->
      <div class="seccion">
        <h3>Horarios de Salida</h3>
        <div class="form-grid">
          <div class="campo">
            <label>Hora inicio salida</label>
            <div class="time-picker" :class="{ 'time-picker-error': erroresHorario.inicio_salida }">
              <select v-model="horasSalida.inicio_h" class="sel-hora">
                <option v-for="h in horas12" :key="h" :value="h">{{ h }}</option>
              </select>
              <span class="sep">:</span>
              <select v-model="horasSalida.inicio_m" class="sel-min">
                <option v-for="m in minutos" :key="m" :value="m">{{ m }}</option>
              </select>
              <select v-model="horasSalida.inicio_ampm" class="sel-ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
            <span class="hint-hora">24h: {{ form.hora_inicio_salida }}</span>
            <span v-if="erroresHorario.inicio_salida" class="error-inline">⚠ {{ erroresHorario.inicio_salida }}</span>
          </div>
          <div class="campo">
            <label>Hora fin salida</label>
            <div class="time-picker" :class="{ 'time-picker-error': erroresHorario.fin_salida }">
              <select v-model="horasSalida.fin_h" class="sel-hora">
                <option v-for="h in horas12" :key="h" :value="h">{{ h }}</option>
              </select>
              <span class="sep">:</span>
              <select v-model="horasSalida.fin_m" class="sel-min">
                <option v-for="m in minutos" :key="m" :value="m">{{ m }}</option>
              </select>
              <select v-model="horasSalida.fin_ampm" class="sel-ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
            <span class="hint-hora">24h: {{ form.hora_fin_salida }}</span>
            <span v-if="erroresHorario.fin_salida" class="error-inline">⚠ {{ erroresHorario.fin_salida }}</span>
          </div>
        </div>
      </div>

      <!-- RECONOCIMIENTO FACIAL: solo SUPERADMIN edita, ADMIN lee -->
      <div class="seccion" :class="{ 'seccion-bloqueada': !auth.esSuperAdmin }">
        <h3>
          Reconocimiento Facial
          <span v-if="!auth.esSuperAdmin" class="badge-solo-superadmin">Solo SuperAdmin</span>
        </h3>
        <div class="campo">
          <label>Umbral de similitud facial (0.0 - 1.0)</label>
          <input v-model="form.umbral_similitud" type="number" min="0" max="1" step="0.05"
            :disabled="!auth.esSuperAdmin" :class="{ 'input-readonly': !auth.esSuperAdmin }" />
          <span class="hint">Valor recomendado: 0.6</span>
        </div>
      </div>

      <!-- CONTROL DE ACCESO: solo SUPERADMIN edita -->
      <div class="seccion" :class="{ 'seccion-bloqueada': !auth.esSuperAdmin }">
        <h3>
          Control de Acceso
          <span v-if="!auth.esSuperAdmin" class="badge-solo-superadmin">Solo SuperAdmin</span>
        </h3>
        <div class="campo">
          <label>IPs autorizadas (separadas por coma)</label>
          <input v-model="form.ip_autorizada" type="text" placeholder="192.168.1.0/24, 10.0.0.0/8"
            :disabled="!auth.esSuperAdmin" :class="{ 'input-readonly': !auth.esSuperAdmin }" />
        </div>
        <div class="campo-toggle" :style="!auth.esSuperAdmin ? 'pointer-events:none;opacity:0.5' : ''">
          <label>Control por IP activo</label>
          <div class="toggle" :class="{ activo: form.control_ip_activo }"
            @click="auth.esSuperAdmin && (form.control_ip_activo = !form.control_ip_activo)">
            <div class="toggle-circulo"></div>
          </div>
        </div>
      </div>

      <!-- SEGURIDAD: solo SUPERADMIN -->
      <div class="seccion" :class="{ 'seccion-bloqueada': !auth.esSuperAdmin }">
        <h3>
          Seguridad
          <span v-if="!auth.esSuperAdmin" class="badge-solo-superadmin">Solo SuperAdmin</span>
        </h3>
        <div class="form-grid">
          <div class="campo">
            <label>Máx. intentos de login</label>
            <input v-model="form.max_intentos" type="number" min="1" max="10" :disabled="!auth.esSuperAdmin"
              :class="{ 'input-readonly': !auth.esSuperAdmin }" />
          </div>
          <div class="campo">
            <label>Máx. intentos faciales</label>
            <input v-model="form.max_intentos_faciales" type="number" min="1" max="10" :disabled="!auth.esSuperAdmin"
              :class="{ 'input-readonly': !auth.esSuperAdmin }" />
          </div>
        </div>
      </div>

      <!-- MENSAJE -->
      <div v-if="exito" class="exito">{{ exito }}</div>
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

      <!-- BOTÓN GUARDAR -->
      <button @click="guardar" :disabled="guardando" class="btn-guardar">
        {{ guardando ? 'Guardando...' : 'Guardar configuración' }}
      </button>

    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const cargando = ref(true)
const guardando = ref(false)
const exito = ref('')
const errorMsg = ref('')
const erroresHorario = ref({})

const form = ref({
  hora_inicio_entrada: '', hora_fin_entrada: '',
  hora_inicio_salida: '', hora_fin_salida: '',
  tolerancia_minutos: 30,
  umbral_similitud: 0.6,
  ip_autorizada: '',
  control_ip_activo: false,
  max_intentos: 5,
  max_intentos_faciales: 5,
})

const horas12 = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0'))
const minutos = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'))

const horasEntrada = reactive({ inicio_h: '07', inicio_m: '00', inicio_ampm: 'AM', fin_h: '08', fin_m: '00', fin_ampm: 'AM' })
const horasSalida = reactive({ inicio_h: '04', inicio_m: '00', inicio_ampm: 'PM', fin_h: '05', fin_m: '00', fin_ampm: 'PM' })

const limiteTolerancia = computed(() => {
  if (!form.value.hora_fin_entrada) return '--'
  const [h, m] = form.value.hora_fin_entrada.split(':').map(Number)
  const totalMinutos = h * 60 + m + (form.value.tolerancia_minutos || 0)
  const hh = Math.floor(totalMinutos / 60) % 24
  const mm = totalMinutos % 60
  const ampm = hh >= 12 ? 'PM' : 'AM'
  const h12 = hh === 0 ? 12 : hh > 12 ? hh - 12 : hh
  return `${String(h12).padStart(2, '0')}:${String(mm).padStart(2, '0')} ${ampm}`
})

function a12h(hora24) {
  if (!hora24) return { h: '07', m: '00', ampm: 'AM' }
  const [hStr, mStr] = hora24.split(':')
  let h = parseInt(hStr)
  const ampm = h >= 12 ? 'PM' : 'AM'
  if (h === 0) h = 12; else if (h > 12) h -= 12
  return { h: String(h).padStart(2, '0'), m: mStr || '00', ampm }
}

function a24h(h, m, ampm) {
  let hNum = parseInt(h)
  if (ampm === 'AM' && hNum === 12) hNum = 0
  else if (ampm === 'PM' && hNum !== 12) hNum += 12
  return `${String(hNum).padStart(2, '0')}:${m}`
}

watch(horasEntrada, () => {
  form.value.hora_inicio_entrada = a24h(horasEntrada.inicio_h, horasEntrada.inicio_m, horasEntrada.inicio_ampm)
  form.value.hora_fin_entrada = a24h(horasEntrada.fin_h, horasEntrada.fin_m, horasEntrada.fin_ampm)
  erroresHorario.value = {}
}, { deep: true })

watch(horasSalida, () => {
  form.value.hora_inicio_salida = a24h(horasSalida.inicio_h, horasSalida.inicio_m, horasSalida.inicio_ampm)
  form.value.hora_fin_salida = a24h(horasSalida.fin_h, horasSalida.fin_m, horasSalida.fin_ampm)
  erroresHorario.value = {}
}, { deep: true })

function inicializarSelectores() {
  const ie = a12h(form.value.hora_inicio_entrada)
  horasEntrada.inicio_h = ie.h; horasEntrada.inicio_m = ie.m; horasEntrada.inicio_ampm = ie.ampm
  const fe = a12h(form.value.hora_fin_entrada)
  horasEntrada.fin_h = fe.h; horasEntrada.fin_m = fe.m; horasEntrada.fin_ampm = fe.ampm
  const is_ = a12h(form.value.hora_inicio_salida)
  horasSalida.inicio_h = is_.h; horasSalida.inicio_m = is_.m; horasSalida.inicio_ampm = is_.ampm
  const fs = a12h(form.value.hora_fin_salida)
  horasSalida.fin_h = fs.h; horasSalida.fin_m = fs.m; horasSalida.fin_ampm = fs.ampm
}

onMounted(async () => {
  try {
    const response = await api.get('/api/configuracion/')
    // El backend devuelve _permisos también, pero los ignoramos y usamos auth store
    const { _permisos, ...config } = response.data
    form.value = { ...form.value, ...config }
    inicializarSelectores()
  } catch (e) {
    errorMsg.value = 'Error al cargar la configuración'
  } finally { cargando.value = false }
})

async function guardar() {
  exito.value = ''; errorMsg.value = ''; erroresHorario.value = {}; guardando.value = true

  // ── Validación de coherencia de horarios ──────────────────────────────────
  const hie = form.value.hora_inicio_entrada
  const hfe = form.value.hora_fin_entrada
  const his = form.value.hora_inicio_salida
  const hfs = form.value.hora_fin_salida

  // Regla 1: inicio_entrada < fin_entrada  → error en fin_entrada
  if (hie && hfe && hie >= hfe) {
    erroresHorario.value.fin_entrada = 'Debe ser posterior a la hora inicio de entrada.'
  }
  // Regla 2: fin_entrada <= inicio_salida  → error en inicio_salida (ese es el campo mal puesto)
  if (hfe && his && his <= hfe) {
    erroresHorario.value.inicio_salida = 'Debe ser posterior a la hora fin de entrada (' + hfe + ').'
  }
  // Regla 3: inicio_salida < fin_salida    → error en fin_salida
  if (his && hfs && his >= hfs) {
    erroresHorario.value.fin_salida = 'Debe ser posterior a la hora inicio de salida.'
  }

  if (Object.keys(erroresHorario.value).length > 0) {
    errorMsg.value = 'Corrige los errores en los horarios antes de guardar.'
    guardando.value = false
    return
  }
  // ─────────────────────────────────────────────────────────────────────────
  try {
    // Construir payload según el rol: ADMIN solo envía horarios y tolerancia
    const payload = {
      hora_inicio_entrada: form.value.hora_inicio_entrada,
      hora_fin_entrada: form.value.hora_fin_entrada,
      hora_inicio_salida: form.value.hora_inicio_salida,
      hora_fin_salida: form.value.hora_fin_salida,
      tolerancia_minutos: form.value.tolerancia_minutos,
    }

    // Solo SUPERADMIN envía estos campos
    if (auth.esSuperAdmin) {
      payload.umbral_similitud = form.value.umbral_similitud
      payload.ip_autorizada = form.value.ip_autorizada
      payload.control_ip_activo = form.value.control_ip_activo
      payload.max_intentos = form.value.max_intentos
      payload.max_intentos_faciales = form.value.max_intentos_faciales
    }

    await api.patch('/api/configuracion/', payload)
    exito.value = 'Configuración guardada correctamente'
    setTimeout(() => exito.value = '', 3000)
  } catch (e) {
    errorMsg.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'Error al guardar la configuración'
  } finally { guardando.value = false }
}
</script>

<style scoped src="./style.css"></style>