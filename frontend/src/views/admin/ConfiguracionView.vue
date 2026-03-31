<!-- ConfiguracionView.vue — Configuración del sistema -->
<!-- Formulario con horarios, umbral facial, IPs y seguridad -->

<template>
  <AdminLayout titulo="Configuración">

    <div v-if="cargando" class="cargando">Cargando configuración...</div>

    <div v-else class="config-container">

      <!-- HORARIOS DE ENTRADA -->
      <div class="seccion">
        <h3>Horarios de Entrada</h3>
        <div class="horario-info">
          <span class="horario-tag">Puntual</span> si llega antes de la hora fin entrada.
          <span class="horario-tag tardanza">Tardanza</span> si llega después.
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
            <div class="time-picker">
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
          </div>
        </div>
      </div>

      <!-- HORARIOS DE SALIDA -->
      <div class="seccion">
        <h3>Horarios de Salida</h3>
        <div class="form-grid">
          <div class="campo">
            <label>Hora inicio salida</label>
            <div class="time-picker">
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
          </div>
          <div class="campo">
            <label>Hora fin salida</label>
            <div class="time-picker">
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
          </div>
        </div>
      </div>

      <!-- RECONOCIMIENTO FACIAL -->
      <div class="seccion">
        <h3>Reconocimiento Facial</h3>
        <div class="campo">
          <label>Umbral de similitud facial (0.0 - 1.0)</label>
          <input v-model="form.umbral_similitud" type="number" min="0" max="1" step="0.05" />
          <span class="hint">Valor recomendado: 0.6</span>
        </div>
      </div>

      <!-- CONTROL DE ACCESO -->
      <div class="seccion">
        <h3>Control de Acceso</h3>
        <div class="campo">
          <label>IPs autorizadas (separadas por coma)</label>
          <input v-model="form.ip_autorizada" type="text" placeholder="192.168.1.0/24, 10.0.0.0/8" />
        </div>
        <div class="campo-toggle">
          <label>Control por IP activo</label>
          <div
            class="toggle"
            :class="{ activo: form.control_ip_activo }"
            @click="form.control_ip_activo = !form.control_ip_activo"
          >
            <div class="toggle-circulo"></div>
          </div>
        </div>
      </div>

      <!-- SEGURIDAD -->
      <div class="seccion">
        <h3>Seguridad</h3>
        <div class="form-grid">
          <div class="campo">
            <label>Máx. intentos de login</label>
            <input v-model="form.max_intentos" type="number" min="1" max="10" />
          </div>
          <div class="campo">
            <label>Máx. intentos faciales</label>
            <input v-model="form.max_intentos_faciales" type="number" min="1" max="10" />
          </div>
        </div>
      </div>

      <!-- MENSAJE -->
      <div v-if="exito" class="exito">{{ exito }}</div>
      <div v-if="error" class="error">{{ error }}</div>

      <!-- BOTÓN GUARDAR -->
      <button @click="guardar" :disabled="guardando" class="btn-guardar">
      {{ guardando ? 'Guardando...' : 'Guardar configuración' }}
      </button>

    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const cargando = ref(true)
const guardando = ref(false)
const exito = ref('')
const error = ref('')

const form = ref({
  hora_inicio_entrada: '',
  hora_fin_entrada: '',
  hora_inicio_salida: '',
  hora_fin_salida: '',
  umbral_similitud: 0.6,
  ip_autorizada: '',
  control_ip_activo: false,
  max_intentos: 5,
  max_intentos_faciales: 5
})

// Opciones para los selectores
const horas12 = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0'))
const minutos = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'))

// Estado reactivo de los selectores AM/PM
const horasEntrada = reactive({ inicio_h: '07', inicio_m: '00', inicio_ampm: 'AM', fin_h: '08', fin_m: '00', fin_ampm: 'AM' })
const horasSalida  = reactive({ inicio_h: '04', inicio_m: '00', inicio_ampm: 'PM', fin_h: '05', fin_m: '00', fin_ampm: 'PM' })

// Convierte HH:MM (24h) a partes 12h
function a12h(hora24) {
  if (!hora24) return { h: '07', m: '00', ampm: 'AM' }
  const [hStr, mStr] = hora24.split(':')
  let h = parseInt(hStr)
  const ampm = h >= 12 ? 'PM' : 'AM'
  if (h === 0) h = 12
  else if (h > 12) h -= 12
  return { h: String(h).padStart(2, '0'), m: mStr || '00', ampm }
}

// Convierte partes 12h a HH:MM (24h)
function a24h(h, m, ampm) {
  let hNum = parseInt(h)
  if (ampm === 'AM' && hNum === 12) hNum = 0
  else if (ampm === 'PM' && hNum !== 12) hNum += 12
  return `${String(hNum).padStart(2, '0')}:${m}`
}

// Cuando cambia cualquier selector → actualizar form (24h)
watch(horasEntrada, () => {
  form.value.hora_inicio_entrada = a24h(horasEntrada.inicio_h, horasEntrada.inicio_m, horasEntrada.inicio_ampm)
  form.value.hora_fin_entrada    = a24h(horasEntrada.fin_h,    horasEntrada.fin_m,    horasEntrada.fin_ampm)
}, { deep: true })

watch(horasSalida, () => {
  form.value.hora_inicio_salida = a24h(horasSalida.inicio_h, horasSalida.inicio_m, horasSalida.inicio_ampm)
  form.value.hora_fin_salida    = a24h(horasSalida.fin_h,    horasSalida.fin_m,    horasSalida.fin_ampm)
}, { deep: true })

// Inicializar selectores desde el valor 24h del backend
function inicializarSelectores() {
  const ie = a12h(form.value.hora_inicio_entrada)
  horasEntrada.inicio_h    = ie.h
  horasEntrada.inicio_m    = ie.m
  horasEntrada.inicio_ampm = ie.ampm

  const fe = a12h(form.value.hora_fin_entrada)
  horasEntrada.fin_h    = fe.h
  horasEntrada.fin_m    = fe.m
  horasEntrada.fin_ampm = fe.ampm

  const is_ = a12h(form.value.hora_inicio_salida)
  horasSalida.inicio_h    = is_.h
  horasSalida.inicio_m    = is_.m
  horasSalida.inicio_ampm = is_.ampm

  const fs = a12h(form.value.hora_fin_salida)
  horasSalida.fin_h    = fs.h
  horasSalida.fin_m    = fs.m
  horasSalida.fin_ampm = fs.ampm
}

onMounted(async () => {
  try {
    const response = await api.get('/api/configuracion/')
    form.value = { ...response.data }
    inicializarSelectores()
  } catch (e) {
    error.value = 'Error al cargar la configuración'
  } finally {
    cargando.value = false
  }
})

async function guardar() {
  exito.value = ''
  error.value = ''
  guardando.value = true
  try {
    // Enviar solo los campos que acepta el serializer
    const payload = {
      hora_inicio_entrada:   form.value.hora_inicio_entrada,
      hora_fin_entrada:      form.value.hora_fin_entrada,
      hora_inicio_salida:    form.value.hora_inicio_salida,
      hora_fin_salida:       form.value.hora_fin_salida,
      umbral_similitud:      form.value.umbral_similitud,
      ip_autorizada:         form.value.ip_autorizada,
      control_ip_activo:     form.value.control_ip_activo,
      max_intentos:          form.value.max_intentos,
      max_intentos_faciales: form.value.max_intentos_faciales,
    }
    await api.patch('/api/configuracion/', payload)
    exito.value = 'Configuración guardada correctamente'
    setTimeout(() => exito.value = '', 3000)
  } catch (e) {
    error.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'Error al guardar la configuración'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.cargando {
  text-align: center;
  padding: 40px;
  color: #666;
}

.config-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.seccion {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.seccion h3 {
  font-size: 1rem;
  color: #1a3a6b;
  font-weight: bold;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.campo label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #555;
}

.campo input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.campo input:focus {
  outline: none;
  border-color: #1a3a6b;
}

.hint {
  font-size: 0.75rem;
  color: #999;
}

/* TOGGLE */
.campo-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.campo-toggle label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #555;
}

.toggle {
  width: 48px;
  height: 26px;
  background: #ddd;
  border-radius: 13px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}

.toggle.activo {
  background: #1a3a6b;
}

.toggle-circulo {
  position: absolute;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  top: 3px;
  left: 3px;
  transition: left 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.toggle.activo .toggle-circulo {
  left: 25px;
}

.exito {
  background: #f0fdf4;
  color: #16a34a;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.88rem;
  border: 1px solid #bbf7d0;
}

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.88rem;
}

.btn-guardar {
  padding: 12px 28px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  align-self: flex-start;
  transition: background 0.2s;
}

.btn-guardar:hover:not(:disabled) { background: #142d54; }
.btn-guardar:disabled { opacity: 0.7; cursor: not-allowed; }

/* TIME PICKER 12H */
.time-picker {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sel-hora, .sel-min, .sel-ampm {
  padding: 7px 6px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #1a3a6b;
  font-weight: 600;
  cursor: pointer;
  background: white;
}

.sel-hora  { width: 58px; }
.sel-min   { width: 58px; }
.sel-ampm  { width: 62px; }

.sel-hora:focus, .sel-min:focus, .sel-ampm:focus {
  outline: none;
  border-color: #1a3a6b;
}

.sep {
  font-weight: bold;
  color: #1a3a6b;
  font-size: 1rem;
}

.hint-hora {
  font-size: 0.72rem;
  color: #9ca3af;
  margin-top: 3px;
  display: block;
}

/* HORARIO INFO */
.horario-info {
  font-size: 0.82rem;
  color: #6b7280;
  margin-bottom: 14px;
}

.horario-tag {
  display: inline-block;
  background: #dcfce7;
  color: #16a34a;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.76rem;
}

.horario-tag.tardanza {
  background: #fef9c3;
  color: #ca8a04;
}
</style>