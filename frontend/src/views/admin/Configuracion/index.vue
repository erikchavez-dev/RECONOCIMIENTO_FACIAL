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
 
      <!-- ══════════════════════════════════════════════════════════════════
           GEOCERCA — Solo SUPERADMIN puede ver y modificar esta sección
           ══════════════════════════════════════════════════════════════════ -->
      <div v-if="auth.esSuperAdmin" class="seccion seccion-geocerca">
        <h3>
          <span class="geocerca-icono"></span>
          Geocerca (Validación de Ubicación)
        </h3>
 
        <div v-if="cargandoGeocerca" class="geocerca-cargando">Cargando configuración de geocerca...</div>
 
        <template v-else>
 
          <!-- Estado de carga de geocerca -->
          <div v-if="errorGeocerca" class="error" style="margin-bottom:12px">{{ errorGeocerca }}</div>
 
          <!-- Toggle principal: activar/desactivar geocerca -->
          <div class="campo-toggle geocerca-toggle-principal">
            <div class="geocerca-toggle-info">
              <label class="geocerca-label-principal">Activar validación por geocerca</label>
              <p class="geocerca-desc">
                Cuando está activa, el trabajador debe encontrarse físicamente dentro del radio
                configurado para poder marcar asistencia. Esto neutraliza el uso de VPN,
                ya que la validación usa el GPS del dispositivo, no la IP.
              </p>
            </div>
            <div class="toggle toggle-lg" :class="{ activo: geocerca.geocerca_activa }"
              @click="geocerca.geocerca_activa = !geocerca.geocerca_activa">
              <div class="toggle-circulo"></div>
            </div>
          </div>
 
          <!-- Panel de configuración detallada (visible siempre, pero con indicador de inactivo) -->
          <div class="geocerca-panel" :class="{ 'geocerca-panel-inactivo': !geocerca.geocerca_activa }">
 
            <div v-if="!geocerca.geocerca_activa" class="geocerca-inactivo-aviso">
              ⚠ La geocerca está desactivada. Configura los parámetros y actívala cuando estés listo.
            </div>
 
            <!-- Coordenadas de referencia -->
            <div class="geocerca-subtitulo">Punto de referencia (sede autorizada)</div>
            <div class="form-grid">
              <div class="campo">
                <label>Latitud de referencia</label>
                <input
                  v-model="geocerca.geocerca_latitud"
                  type="number"
                  step="0.0000001"
                  placeholder="Ej: -7.1638000"
                  class="input-coords"
                  :class="{ 'input-error': erroresGeocerca.latitud }"
                />
                <span v-if="erroresGeocerca.latitud" class="error-inline">⚠ {{ erroresGeocerca.latitud }}</span>
                <span class="hint">Formato decimal. Negativo = sur del Ecuador.</span>
              </div>
              <div class="campo">
                <label>Longitud de referencia</label>
                <input
                  v-model="geocerca.geocerca_longitud"
                  type="number"
                  step="0.0000001"
                  placeholder="Ej: -78.5000000"
                  class="input-coords"
                  :class="{ 'input-error': erroresGeocerca.longitud }"
                />
                <span v-if="erroresGeocerca.longitud" class="error-inline">⚠ {{ erroresGeocerca.longitud }}</span>
                <span class="hint">Formato decimal. Negativo = oeste del meridiano.</span>
              </div>
            </div>
 
            <!-- Botón de ayuda para obtener coordenadas -->
            <button class="btn-obtener-coords" type="button" @click="obtenerMiUbicacion">
              Usar mi ubicación actual
            </button>
            <span v-if="mensajeUbicacion" class="ubicacion-feedback" :class="{ 'ubicacion-error': errorUbicacion }">
              {{ mensajeUbicacion }}
            </span>
 
            <!-- Radio permitido -->
            <div class="geocerca-subtitulo" style="margin-top:20px">Radio permitido</div>
            <div class="campo">
              <label>Radio máximo en metros</label>
              <div class="radio-row">
                <input
                  v-model.number="geocerca.geocerca_radio_metros"
                  type="number"
                  min="10"
                  max="5000"
                  step="10"
                  class="input-radio-metros"
                  :class="{ 'input-error': erroresGeocerca.radio }"
                />
                <span class="radio-hint">metros</span>
                <span class="radio-badge" :class="radioBadgeClass">{{ radioBadgeLabel }}</span>
              </div>
              <span v-if="erroresGeocerca.radio" class="error-inline">⚠ {{ erroresGeocerca.radio }}</span>
              <span class="hint">Mínimo 10m.</span>
            </div>
 
            <!-- Opciones adicionales -->
            <div class="geocerca-subtitulo" style="margin-top:20px">⚙ Opciones adicionales</div>
 
            <div class="campo-toggle" style="margin-bottom:12px">
              <div>
                <label>Geolocalización obligatoria</label>
                <p class="hint" style="margin:2px 0 0">
                  Si está activo: si el trabajador deniega el GPS, la marcación se rechaza.
                </p>
              </div>
              <div class="toggle" :class="{ activo: geocerca.geocerca_obligatoria }"
                @click="geocerca.geocerca_obligatoria = !geocerca.geocerca_obligatoria">
                <div class="toggle-circulo"></div>
              </div>
            </div>
 
            <div class="campo-toggle">
              <div>
                <label>Registrar auditoría de ubicación</label>
                <p class="hint" style="margin:2px 0 0">
                  Si está activo: cada intento de marcación guarda lat/lon, distancia, IP y dispositivo en auditoría.
                </p>
              </div>
              <div class="toggle" :class="{ activo: geocerca.geocerca_auditoria }"
                @click="geocerca.geocerca_auditoria = !geocerca.geocerca_auditoria">
                <div class="toggle-circulo"></div>
              </div>
            </div>
 
          </div>
          <!-- fin geocerca-panel -->
 
          <!-- Mensajes de geocerca -->
          <div v-if="exitoGeocerca" class="exito" style="margin-top:12px">{{ exitoGeocerca }}</div>
          <div v-if="errorGuardadoGeocerca" class="error" style="margin-top:12px">{{ errorGuardadoGeocerca }}</div>
 
          <!-- Botón guardar geocerca (separado del botón general) -->
          <button @click="guardarGeocerca" :disabled="guardandoGeocerca" class="btn-guardar btn-guardar-geocerca">
            {{ guardandoGeocerca ? 'Guardando geocerca...' : 'Guardar configuración de geocerca' }}
          </button>
 
        </template>
      </div>
      <!-- fin sección geocerca -->
 
      <!-- MENSAJE GENERAL -->
      <div v-if="exito" class="exito">{{ exito }}</div>
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
 
      <!-- BOTÓN GUARDAR GENERAL -->
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
const cargando         = ref(true)
const guardando        = ref(false)
const exito            = ref('')
const errorMsg         = ref('')
const erroresHorario   = ref({})
 
// ── Estado para geocerca ───────────────────────────────────────────────────
const cargandoGeocerca      = ref(true)
const guardandoGeocerca     = ref(false)
const exitoGeocerca         = ref('')
const errorGeocerca         = ref('')
const errorGuardadoGeocerca = ref('')
const erroresGeocerca       = ref({})
const mensajeUbicacion      = ref('')
const errorUbicacion        = ref(false)
 
// ── Formulario general ─────────────────────────────────────────────────────
const form = ref({
  hora_inicio_entrada: '', hora_fin_entrada: '',
  hora_inicio_salida: '',  hora_fin_salida: '',
  tolerancia_minutos: 30,
  umbral_similitud: 0.6,
  ip_autorizada: '',
  control_ip_activo: false,
  max_intentos: 5,
  max_intentos_faciales: 5,
})
 
// ── Formulario geocerca (endpoint separado /api/configuracion/geocerca/) ───
const geocerca = reactive({
  geocerca_activa:       false,
  geocerca_latitud:      null,
  geocerca_longitud:     null,
  geocerca_radio_metros: 100,
  geocerca_obligatoria:  true,
  geocerca_auditoria:    true,
})
 
// ── Helpers de horario ─────────────────────────────────────────────────────
const horas12 = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0'))
const minutos = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'))
 
const horasEntrada = reactive({ inicio_h: '07', inicio_m: '00', inicio_ampm: 'AM', fin_h: '08', fin_m: '00', fin_ampm: 'AM' })
const horasSalida  = reactive({ inicio_h: '04', inicio_m: '00', inicio_ampm: 'PM', fin_h: '05', fin_m: '00', fin_ampm: 'PM' })
 
const limiteTolerancia = computed(() => {
  if (!form.value.hora_fin_entrada) return '--'
  const [h, m] = form.value.hora_fin_entrada.split(':').map(Number)
  const totalMinutos = h * 60 + m + (form.value.tolerancia_minutos || 0)
  const hh   = Math.floor(totalMinutos / 60) % 24
  const mm   = totalMinutos % 60
  const ampm = hh >= 12 ? 'PM' : 'AM'
  const h12  = hh === 0 ? 12 : hh > 12 ? hh - 12 : hh
  return `${String(h12).padStart(2, '0')}:${String(mm).padStart(2, '0')} ${ampm}`
})
 
// Badge visual del radio configurado
const radioBadgeLabel = computed(() => {
  const r = geocerca.geocerca_radio_metros
  if (!r) return ''
  if (r <= 50)  return 'Muy estricto'
  if (r <= 150) return 'Recomendado'
  if (r <= 500) return 'Amplio'
  return 'Muy amplio'
})
const radioBadgeClass = computed(() => {
  const r = geocerca.geocerca_radio_metros
  if (!r) return ''
  if (r <= 50)  return 'badge-estricto'
  if (r <= 150) return 'badge-ok'
  if (r <= 500) return 'badge-amplio'
  return 'badge-muyamplio'
})
 
// ── Conversión 12h / 24h ───────────────────────────────────────────────────
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
  form.value.hora_fin_entrada    = a24h(horasEntrada.fin_h,    horasEntrada.fin_m,    horasEntrada.fin_ampm)
  erroresHorario.value = {}
}, { deep: true })
 
watch(horasSalida, () => {
  form.value.hora_inicio_salida = a24h(horasSalida.inicio_h, horasSalida.inicio_m, horasSalida.inicio_ampm)
  form.value.hora_fin_salida    = a24h(horasSalida.fin_h,    horasSalida.fin_m,    horasSalida.fin_ampm)
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
 
// ── Carga inicial ──────────────────────────────────────────────────────────
onMounted(async () => {
  // Configuración general (ADMIN + SUPERADMIN)
  try {
    const response = await api.get('/api/configuracion/')
    const { _permisos, ...config } = response.data
    form.value = { ...form.value, ...config }
    inicializarSelectores()
  } catch {
    errorMsg.value = 'Error al cargar la configuración'
  } finally {
    cargando.value = false
  }
 
  // Configuración de geocerca (solo SUPERADMIN)
  if (auth.esSuperAdmin) {
    try {
      const res = await api.get('/api/configuracion/geocerca/')
      Object.assign(geocerca, res.data)
    } catch {
      errorGeocerca.value = 'Error al cargar la configuración de geocerca'
    } finally {
      cargandoGeocerca.value = false
    }
  }
})
 
// ── Guardar configuración general ─────────────────────────────────────────
async function guardar() {
  exito.value = ''; errorMsg.value = ''; erroresHorario.value = {}; guardando.value = true
 
  const hie = form.value.hora_inicio_entrada
  const hfe = form.value.hora_fin_entrada
  const his = form.value.hora_inicio_salida
  const hfs = form.value.hora_fin_salida
 
  if (hie && hfe && hie >= hfe)
    erroresHorario.value.fin_entrada = 'Debe ser posterior a la hora inicio de entrada.'
  if (hfe && his && his <= hfe)
    erroresHorario.value.inicio_salida = 'Debe ser posterior a la hora fin de entrada (' + hfe + ').'
  if (his && hfs && his >= hfs)
    erroresHorario.value.fin_salida = 'Debe ser posterior a la hora inicio de salida.'
 
  if (Object.keys(erroresHorario.value).length > 0) {
    errorMsg.value = 'Corrige los errores en los horarios antes de guardar.'
    guardando.value = false
    return
  }
 
  try {
    const payload = {
      hora_inicio_entrada: form.value.hora_inicio_entrada,
      hora_fin_entrada:    form.value.hora_fin_entrada,
      hora_inicio_salida:  form.value.hora_inicio_salida,
      hora_fin_salida:     form.value.hora_fin_salida,
      tolerancia_minutos:  form.value.tolerancia_minutos,
    }
    if (auth.esSuperAdmin) {
      payload.umbral_similitud      = form.value.umbral_similitud
      payload.ip_autorizada         = form.value.ip_autorizada
      payload.control_ip_activo     = form.value.control_ip_activo
      payload.max_intentos          = form.value.max_intentos
      payload.max_intentos_faciales = form.value.max_intentos_faciales
    }
    await api.patch('/api/configuracion/', payload)
    exito.value = 'Configuración guardada correctamente'
    setTimeout(() => exito.value = '', 3000)
  } catch (e) {
    errorMsg.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'Error al guardar la configuración'
  } finally {
    guardando.value = false
  }
}
 
// ── Guardar geocerca (endpoint exclusivo SUPERADMIN) ───────────────────────
async function guardarGeocerca() {
  exitoGeocerca.value = ''; errorGuardadoGeocerca.value = ''; erroresGeocerca.value = {}
  guardandoGeocerca.value = true
 
  // Validación frontend
  if (geocerca.geocerca_activa) {
    if (!geocerca.geocerca_latitud && geocerca.geocerca_latitud !== 0)
      erroresGeocerca.value.latitud = 'La latitud es obligatoria cuando la geocerca está activa.'
    if (!geocerca.geocerca_longitud && geocerca.geocerca_longitud !== 0)
      erroresGeocerca.value.longitud = 'La longitud es obligatoria cuando la geocerca está activa.'
  }
  if (geocerca.geocerca_radio_metros < 10)
    erroresGeocerca.value.radio = 'El radio mínimo es 10 metros.'
 
  if (Object.keys(erroresGeocerca.value).length > 0) {
    guardandoGeocerca.value = false
    return
  }
 
  try {
    await api.patch('/api/configuracion/geocerca/', {
      geocerca_activa:       geocerca.geocerca_activa,
      geocerca_latitud:      geocerca.geocerca_latitud,
      geocerca_longitud:     geocerca.geocerca_longitud,
      geocerca_radio_metros: geocerca.geocerca_radio_metros,
      geocerca_obligatoria:  geocerca.geocerca_obligatoria,
      geocerca_auditoria:    geocerca.geocerca_auditoria,
    })
    exitoGeocerca.value = '✓ Geocerca guardada correctamente'
    setTimeout(() => exitoGeocerca.value = '', 3000)
  } catch (e) {
    errorGuardadoGeocerca.value =
      e.response?.data?.non_field_errors?.[0] ||
      e.response?.data?.error ||
      JSON.stringify(e.response?.data) ||
      'Error al guardar la geocerca'
  } finally {
    guardandoGeocerca.value = false
  }
}
 
// ── Obtener ubicación actual como referencia ───────────────────────────────
function obtenerMiUbicacion() {
  mensajeUbicacion.value = 'Obteniendo ubicación...'
  errorUbicacion.value   = false
 
  if (!navigator.geolocation) {
    mensajeUbicacion.value = 'Tu navegador no soporta geolocalización.'
    errorUbicacion.value   = true
    return
  }
 
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      geocerca.geocerca_latitud  = parseFloat(pos.coords.latitude.toFixed(7))
      geocerca.geocerca_longitud = parseFloat(pos.coords.longitude.toFixed(7))
      mensajeUbicacion.value     = `✓ Coordenadas obtenidas: ${geocerca.geocerca_latitud}, ${geocerca.geocerca_longitud}`
      errorUbicacion.value       = false
      setTimeout(() => mensajeUbicacion.value = '', 5000)
    },
    (err) => {
      const msgs = {
        1: 'Permiso de ubicación denegado.',
        2: 'No se pudo determinar la ubicación.',
        3: 'Tiempo de espera agotado.',
      }
      mensajeUbicacion.value = msgs[err.code] || 'Error al obtener ubicación.'
      errorUbicacion.value   = true
    },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}
</script>
 
<style scoped src="./style.css"></style>