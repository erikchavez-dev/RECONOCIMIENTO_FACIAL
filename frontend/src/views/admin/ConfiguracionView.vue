<!-- ConfiguracionView.vue — Configuración del sistema -->
<!-- Formulario con horarios, umbral facial, IPs y seguridad -->

<template>
  <AdminLayout titulo="Configuración">

    <div v-if="cargando" class="cargando">Cargando configuración...</div>

    <div v-else class="config-container">

      <!-- HORARIOS DE ENTRADA -->
      <div class="seccion">
        <h3>Horarios de Entrada</h3>
        <div class="form-grid">
          <div class="campo">
            <label>Hora inicio entrada</label>
            <input v-model="form.hora_inicio_entrada" type="time" />
          </div>
          <div class="campo">
            <label>Hora fin entrada</label>
            <input v-model="form.hora_fin_entrada" type="time" />
          </div>
        </div>
      </div>

      <!-- HORARIOS DE SALIDA -->
      <div class="seccion">
        <h3>Horarios de Salida</h3>
        <div class="form-grid">
          <div class="campo">
            <label>Hora inicio salida</label>
            <input v-model="form.hora_inicio_salida" type="time" />
          </div>
          <div class="campo">
            <label>Hora fin salida</label>
            <input v-model="form.hora_fin_salida" type="time" />
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
import { ref, onMounted } from 'vue'
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

onMounted(async () => {
  try {
    const response = await api.get('/api/configuracion/')
    form.value = { ...response.data }
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
    await api.patch('/api/configuracion/', form.value)
    exito.value = 'Configuración guardada correctamente'
    setTimeout(() => exito.value = '', 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al guardar la configuración'
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
</style>