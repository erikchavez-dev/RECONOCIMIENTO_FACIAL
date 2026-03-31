<template>
  <AdminLayout titulo="Trabajadores">

    <div class="toolbar">
      <h3>Gestión de Trabajadores</h3>
      <button @click="abrirModalCrear" class="btn-nuevo">+ Nuevo Trabajador</button>
    </div>

    <!-- TABLA -->
    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Foto</th>
            <th>Nombre</th>
            <th>DNI</th>
            <th>Cargo</th>
            <th>Estado</th>
            <th>Embedding</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in trabajadores" :key="t.id">
            <td>
              <img
                :src="t.foto_url ? `http://127.0.0.1:8000${t.foto_url}` : '/sin-foto.png'"
                class="foto-trabajador"
                alt="Foto"
              />
            </td>
            <td>{{ t.apellido_paterno }} {{ t.apellido_materno  }} {{t.nombres }}</td>
            <td>{{ t.dni }}</td>
            <td>{{ t.cargo }}</td>
            <td>
              <span :class="['badge', estadoBadgeClass(t)]">
                {{ estadoBadgeTexto(t) }}
              </span>
            </td>
            <td>
              <span :class="['badge', t.embedding ? 'badge-si' : 'badge-no']">
                {{ t.embedding ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="acciones">
              <!-- BOTÓN EDITAR -->
              <button @click="abrirModalEditar(t)" class="btn-accion" title="Editar">
                <img :src="iconoEditar" alt="Editar" width="18" height="18" />
              </button>

              <!-- INTERRUPTOR: deshabilitado si contrato vencido -->
              <label class="switch-button" :title="contratoVencido(t) ? 'Contrato vencido — no se puede activar' : ''">
                <input
                  type="checkbox"
                  :checked="t.activo"
                  :disabled="contratoVencido(t)"
                  @change="toggleActivo(t)"
                >
                <span class="slider-round" :class="{ 'slider-disabled': contratoVencido(t) }"></span>
              </label>

              <!-- BOTÓN ELIMINAR -->
              <button @click="eliminar(t)" class="btn-accion delete" title="Eliminar">
                <img :src="iconBasura" alt="Eliminar" width="18" height="18" />
              </button>
            </td>

          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL CREAR/EDITAR -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <h3>{{ modoEdicion ? 'Editar Trabajador' : 'Nuevo Trabajador' }}</h3>

        <!-- PASO 1: DATOS -->
        <div v-if="paso === 1">
          <div class="form-grid">
            <div class="campo">
              <label>Nombres</label>
              <input v-model="form.nombres" type="text" placeholder="Nombres" />
            </div>
            <div class="campo">
              <label>Apellido Paterno</label>
              <input v-model="form.apellido_paterno" type="text" placeholder="Apellido Paterno" />
            </div>
            <div class="campo">
              <label>Apellido Materno</label>
              <input v-model="form.apellido_materno" type="text" placeholder="Apellido Materno" />
            </div>
            <div class="campo">
              <label>DNI</label>
              <input v-model="form.dni" type="text" maxlength="8" placeholder="DNI" :disabled="modoEdicion" />
            </div>
            <div class="campo">
              <label>Teléfono</label>
              <input v-model="form.telefono" type="text" placeholder="Teléfono" />
            </div>
            <div class="campo">
              <label>Cargo</label>
              <input v-model="form.cargo" type="text" placeholder="Cargo" />
            </div>
            <div class="campo">
              <label>Fecha inicio laboral</label>
              <input v-model="form.fecha_inicio_laboral" type="date" />
            </div>
            <div class="campo" v-if="!modoEdicion">
              <label>Rol</label>
              <select v-model="form.rol">
                <option value="TRABAJADOR">Trabajador</option>
                <option value="ADMIN">Administrador</option>
              </select>
            </div>
          </div>

          <div v-if="errorModal" class="error">{{ errorModal }}</div>

          <div class="modal-acciones">
            <button @click="cerrarModal" class="btn-cancelar">Cancelar</button>
            <button @click="modoEdicion ? guardar() : siguientePaso()" :disabled="guardando" class="btn-guardar">
              {{ modoEdicion ? (guardando ? 'Guardando...' : 'Guardar') : 'Siguiente →' }}
            </button>
          </div>
        </div>

        <!-- PASO 2: FOTOS (solo al crear) -->
        <div v-if="paso === 2">
          <p class="instruccion-fotos">
            Capture o cargue <strong>3 fotos</strong> del trabajador. La primera será su foto de perfil.
          </p>

          <!-- OPCIONES -->
          <div class="opciones-foto">
            <button
              @click="modoFoto = 'camara'"
              :class="['btn-opcion', modoFoto === 'camara' ? 'activo' : '']">
            Usar cámara
            </button>
            <button
              @click="modoFoto = 'archivo'"
              :class="['btn-opcion', modoFoto === 'archivo' ? 'activo' : '']"
            >
            Cargar imágenes
            </button>
          </div>

          <!-- CÁMARA -->
          <div v-if="modoFoto === 'camara'" class="camara-section">
            <div class="camara-wrapper">
              <video ref="videoRef" autoplay playsinline class="video"></video>
              <canvas ref="canvasRef" style="display:none"></canvas>
            </div>
            <button @click="capturarFoto" :disabled="fotosCapturadas.length >= 3" class="btn-capturar">
              Capturar foto ({{ fotosCapturadas.length }}/3)
            </button>
          </div>

          <!-- CARGAR ARCHIVOS -->
          <div v-if="modoFoto === 'archivo'" class="archivo-section">
            <input
              type="file"
              accept="image/*"
              multiple
              @change="cargarArchivos"
              ref="inputArchivo"
              style="display:none"
            />
            <button @click="$refs.inputArchivo.click()" class="btn-cargar">
            Seleccionar 3 imágenes
            </button>
            <p class="hint">Seleccione exactamente 3 imágenes</p>
          </div>

          <!-- PREVIEW FOTOS -->
          <div v-if="fotosCapturadas.length > 0" class="fotos-preview">
            <div v-for="(foto, i) in fotosCapturadas" :key="i" class="foto-preview-item">
              <img :src="foto" alt="Foto" />
              <span class="foto-label">{{ i === 0 ? '⭐ Perfil' : `Foto ${i + 1}` }}</span>
              <button @click="eliminarFoto(i)" class="btn-eliminar-foto">✕</button>
            </div>
          </div>

          <div v-if="errorModal" class="error">{{ errorModal }}</div>
          <div v-if="procesando" class="procesando">Registrando embedding... por favor espere</div>

          <div class="modal-acciones">
            <button @click="paso = 1" class="btn-cancelar">← Volver</button>
            <button
              @click="guardarConFotos"
              :disabled="fotosCapturadas.length !== 3 || procesando"
              class="btn-guardar"
            >
              {{ procesando ? 'Procesando...' : 'Guardar trabajador' }}
            </button>
          </div>
        </div>

      </div>
    </div>

  </AdminLayout>
</template>

<script setup>
import iconoEditar from '@/assets/icon-lapicito.svg'
import iconBasura from '@/assets/icon-basura.svg'

import { ref, onMounted, watch } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const trabajadores = ref([])
const cargando = ref(true)
const mostrarModal = ref(false)
const modoEdicion = ref(false)
const guardando = ref(false)
const procesando = ref(false)
const errorModal = ref('')
const trabajadorSeleccionado = ref(null)
const paso = ref(1)
const modoFoto = ref('camara')
const fotosCapturadas = ref([])
const videoRef = ref(null)
const canvasRef = ref(null)
const inputArchivo = ref(null)
let stream = null

const form = ref({
  nombres: '', apellido_paterno: '', apellido_materno: '',
  dni: '', telefono: '', cargo: '', fecha_inicio_laboral: '',
  rol: 'TRABAJADOR'
})

onMounted(async () => {
  await cargarTrabajadores()
})

async function cargarTrabajadores() {
  cargando.value = true
  try {
    const response = await api.get('/api/trabajadores/')
    trabajadores.value = response.data
  } catch (e) {
    console.error('Error:', e)
  } finally {
    cargando.value = false
  }
}

function abrirModalCrear() {
  modoEdicion.value = false
  paso.value = 1
  fotosCapturadas.value = []
  errorModal.value = ''
  form.value = {
    nombres: '', apellido_paterno: '', apellido_materno: '',
    dni: '', telefono: '', cargo: '', fecha_inicio_laboral: '',
    rol: 'TRABAJADOR'
  }
  mostrarModal.value = true
}

function abrirModalEditar(t) {
  modoEdicion.value = true
  paso.value = 1
  trabajadorSeleccionado.value = t
  form.value = {
    nombres: t.nombres,
    apellido_paterno: t.apellido_paterno,
    apellido_materno: t.apellido_materno,
    dni: t.dni,
    telefono: t.telefono || '',
    cargo: t.cargo,
    fecha_inicio_laboral: t.fecha_inicio_laboral?.split('T')[0] || '',
    rol: 'TRABAJADOR'
  }
  errorModal.value = ''
  mostrarModal.value = true
}

function cerrarModal() {
  detenerCamara()
  mostrarModal.value = false
  errorModal.value = ''
  fotosCapturadas.value = []
  paso.value = 1
}

async function siguientePaso() {
  if (!form.value.nombres || !form.value.apellido_paterno || !form.value.dni || !form.value.cargo || !form.value.fecha_inicio_laboral) {
    errorModal.value = 'Complete todos los campos obligatorios'
    return
  }
  errorModal.value = ''
  paso.value = 2
  // Iniciar cámara si está en modo cámara
  if (modoFoto.value === 'camara') {
    await iniciarCamara()
  }
}

// Observar cambio de modo foto
watch(modoFoto, async (nuevo) => {
  if (nuevo === 'camara') {
    await iniciarCamara()
  } else {
    detenerCamara()
  }
})

async function iniciarCamara() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 480 }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (e) {
    errorModal.value = 'No se pudo acceder a la cámara'
    modoFoto.value = 'archivo'
  }
}

function detenerCamara() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
}

function capturarFoto() {
  if (fotosCapturadas.value.length >= 3) return
  const canvas = canvasRef.value
  const video = videoRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  const foto = canvas.toDataURL('image/jpeg', 0.8)
  fotosCapturadas.value.push(foto)
}

function cargarArchivos(event) {
  const files = Array.from(event.target.files)
  if (files.length !== 3) {
    errorModal.value = 'Debe seleccionar exactamente 3 imágenes'
    return
  }
  errorModal.value = ''
  fotosCapturadas.value = []
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      fotosCapturadas.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
}

function eliminarFoto(index) {
  fotosCapturadas.value.splice(index, 1)
}

async function guardar() {
  errorModal.value = ''
  guardando.value = true
  try {
    await api.patch(`/api/trabajadores/${trabajadorSeleccionado.value.id}/`, form.value)
    cerrarModal()
    await cargarTrabajadores()
  } catch (e) {
    console.log('Error detallado:', e.response?.data)
    errorModal.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'Error al procesar las fotos'
  } finally {
    guardando.value = false
  }
}

async function guardarConFotos() {
  if (fotosCapturadas.value.length !== 3) {
    errorModal.value = 'Se necesitan exactamente 3 fotos'
    return
  }
  errorModal.value = ''
  procesando.value = true

  try {
    // 1. Crear trabajador
    const response = await api.post('/api/trabajadores/', {
      nombres: form.value.nombres,
      apellido_paterno: form.value.apellido_paterno,
      apellido_materno: form.value.apellido_materno,
      dni: form.value.dni,
      telefono: form.value.telefono,
      cargo: form.value.cargo,
      fecha_inicio_laboral: form.value.fecha_inicio_laboral,
    })
    const trabajador = response.data

    // 2. Subir foto de perfil (primera foto)
    await api.post(`/api/trabajadores/${trabajador.id}/foto/`, {
      imagen: fotosCapturadas.value[0]
    })

    // 3. Registrar embedding (3 fotos)
    await api.post('/api/reconocimiento/registrar-embedding/', {
      trabajador_id: trabajador.id,
      imagenes: fotosCapturadas.value
    })

    // 4. Si el rol es ADMIN, actualizar el usuario
    if (form.value.rol === 'ADMIN') {
      const usuarios = await api.get('/api/auth/listar/')
      const usuario = usuarios.data.usuarios.find(u => u.trabajador_id === trabajador.id || u.dni === trabajador.dni)
      // El rol se asigna automáticamente como TRABAJADOR al crear
      // Para cambiar a ADMIN necesitaríamos un endpoint adicional
    }

    detenerCamara()
    cerrarModal()
    await cargarTrabajadores()

  } catch (e) {
    errorModal.value = e.response?.data?.error || 'Error al procesar las fotos'
  } finally {
    procesando.value = false
  }
}

// Verifica si el contrato del trabajador ya venció
function contratoVencido(t) {
  if (!t.fecha_fin_laboral) return false
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  const fin = new Date(t.fecha_fin_laboral + 'T00:00:00')
  return fin < hoy
}

// Clase CSS del badge de estado
function estadoBadgeClass(t) {
  if (contratoVencido(t)) return 'badge-vencido'
  if (t.activo_efectivo) return 'badge-activo'
  return 'badge-inactivo'
}

// Texto del badge de estado
function estadoBadgeTexto(t) {
  if (contratoVencido(t)) return 'Vencido'
  if (t.activo_efectivo) return 'Activo'
  return 'Inactivo'
}

async function toggleActivo(t) {
  if (contratoVencido(t)) return
  try {
    await api.patch(`/api/trabajadores/${t.id}/activar-desactivar/`)
    await cargarTrabajadores()
  } catch (e) {
    alert('Error al cambiar estado')
  }
}

async function eliminar(t) {
  if (!confirm(`¿Eliminar a ${t.nombres} ${t.apellido_paterno}?`)) return
  
  try {
    await api.delete(`/api/trabajadores/${t.id}/`)
    await cargarTrabajadores()
  } catch (e) {
    const data = e.response?.data
    
    // Si tiene marcaciones preguntar si forzar
    if (data?.tiene_marcaciones) {
      const forzar = confirm(
        `El trabajador ${t.nombres} ${t.apellido_paterno} tiene marcaciones registradas.\n\n` +
        `¿Desea eliminarlo de todas formas junto con todas sus marcaciones?`
      )
      if (!forzar) return

      try {
        await api.delete(`/api/trabajadores/${t.id}/`, { data: { forzar: true } })
        await cargarTrabajadores()
      } catch (e2) {
        alert(e2.response?.data?.error || 'Error al eliminar')
      }
    } else {
      alert(data?.error || 'Error al eliminar')
    }
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar h3 { font-size: 1.1rem; color: #1a3a6b; }

.btn-nuevo {
  background: #1a3a6b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-nuevo:hover { background: #142d54; }

.tabla-container {
  background: white;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.88rem; }

.tabla th {
  background: #1a3a6b;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.tabla td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.tabla tr:hover { background: #f8fafc; }

.foto-trabajador {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background: #e5e7eb;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}

.badge-activo { background: #dcfce7; color: #16a34a; }
.badge-inactivo { background: #fee2e2; color: #dc2626; }
.badge-vencido { background: #fef3c7; color: #b45309; }
.badge-si { background: #dbeafe; color: #1d4ed8; }
.badge-no { background: #f3f4f6; color: #6b7280; }

.acciones { display: flex; gap: 6px; }

.btn-accion {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 4px;
  border-radius: 4px;
}

.btn-accion:hover { background: #f0f4f8; }

.cargando { text-align: center; padding: 40px; color: #666; }

/* MODAL */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 { font-size: 1.1rem; color: #1a3a6b; margin-bottom: 20px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.campo label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #1a3a6b;
  margin-bottom: 4px;
}

.campo input, .campo select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.88rem;
  box-sizing: border-box;
}

.campo input:focus, .campo select:focus {
  outline: none;
  border-color: #1a3a6b;
}

.campo input:disabled { background: #f3f4f6; color: #999; }

/* FOTOS */
.instruccion-fotos {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 16px;
  text-align: center;
}

.opciones-foto {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  justify-content: center;
}

.btn-opcion {
  padding: 8px 20px;
  border: 2px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.2s;
  display: flex;     
  align-items: center;  
  justify-content: center; 
  gap: 8px;   
}

.btn-opcion.activo {
  border-color: #1a3a6b;
  background: #1a3a6b;
  color: white;
}

.camara-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.camara-wrapper {
  border-radius: 8px;
  overflow: hidden;
}

.video {
  width: 100%;
  max-width: 360px;
  display: block;
}

.btn-capturar {
  padding: 10px 24px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-capturar:disabled { opacity: 0.5; cursor: not-allowed; }

.archivo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.btn-cargar {
  padding: 10px 24px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.hint { font-size: 0.8rem; color: #999; }

.fotos-preview {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.foto-preview-item {
  position: relative;
  text-align: center;
}

.foto-preview-item img {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #1a3a6b;
}

.foto-label {
  display: block;
  font-size: 0.75rem;
  color: #555;
  margin-top: 4px;
}

.btn-eliminar-foto {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.procesando {
  text-align: center;
  color: #1a3a6b;
  font-size: 0.88rem;
  padding: 8px;
  background: #dbeafe;
  border-radius: 6px;
  margin-bottom: 12px;
}

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  margin-bottom: 16px;
}

.modal-acciones {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.btn-cancelar {
  padding: 10px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-guardar {
  padding: 10px 24px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-guardar:disabled { opacity: 0.7; cursor: not-allowed; }

/* Contenedor del switch */
.switch-button {
  position: relative;
  display: inline-block;
  width: 42px;
  height: 22px;
  vertical-align: middle;
}

/* Ocultar el checkbox original */
.switch-button input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* El fondo del switch */
.slider-round {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #cbd5e1; /* Gris cuando está apagado */
  transition: .4s;
  border-radius: 24px;
}

/* El círculo blanco que se mueve */
.slider-round:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Color naranja cuando está activado (combinando con tu menú) */
input:checked + .slider-round {
  background-color: #16a34a; 
}

/* Movimiento del círculo al activar */
input:checked + .slider-round:before {
  transform: translateX(20px);
}

/* Efecto de foco para accesibilidad */
input:focus + .slider-round {
  box-shadow: 0 0 1px #ff7300;
}

/* Switch deshabilitado cuando contrato vencido */
.slider-round.slider-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icono-camara {
  width: 26px;
  height: 26px;
  margin-right: 6px;
}

</style>