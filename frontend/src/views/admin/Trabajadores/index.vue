<template>
  <AdminLayout titulo="Trabajadores">

    <div class="toolbar">
      <h3>Gestión de Trabajadores</h3>
      <div class="buscador">
        <div class="buscador-input">
          <img :src="iconoLupa" class="icono-buscar" alt="Buscar" />
          <input v-model="buscar" @input="buscarTrabajadores" type="text"
          placeholder="Ingrese DNI, nombre o apellido" class="input-buscar" />
        </div>
      </div>
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
          <tr v-for="t in trabajadoresPaginados" :key="t.id">
            <td>
              <img :src="t.foto_url ? `http://127.0.0.1:8000${t.foto_url}` : '/sin-foto.png'" class="foto-trabajador"
                alt="Foto" />
            </td>
            <td>{{ t.apellido_paterno }} {{ t.apellido_materno }} {{ t.nombres }}</td>
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
                <img :src="iconoEditar" alt="Editar" width="22" height="22" />
              </button>

              <!-- INTERRUPTOR: deshabilitado si contrato vencido -->
              <label class="switch-button" :title="contratoVencido(t) ? 'Contrato vencido — no se puede activar' : ''">
                <input type="checkbox" :checked="t.activo" :disabled="contratoVencido(t)" @change="toggleActivo(t)">
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
    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="paginaActual = 1" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">«</button>

      <button @click="paginaActual--" :disabled="paginaActual === 1" class="btn-pagina">
        ‹ Anterior
      </button>

      <div class="paginas-numeros">
        <button v-for="p in paginasVisibles" :key="p" @click="paginaActual = p"
          :class="['btn-num', p === paginaActual ? 'activo' : '']">
          {{ p }}
        </button>
      </div>

      <button @click="paginaActual++" :disabled="paginaActual === totalPaginas" class="btn-pagina">
        Siguiente ›
      </button>

      <button @click="paginaActual = totalPaginas" :disabled="paginaActual === totalPaginas"
        class="btn-pagina btn-extremo">
        »
      </button>
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
              <input v-model="form.telefono" type="text" maxlength="9" placeholder="Teléfono" />
            </div>
            <div class="campo">
              <label>Cargo</label>
              <input v-model="form.cargo" type="text" placeholder="Cargo" />
            </div>
            <div class="campo">
              <label>Fecha inicio laboral</label>
              <input v-model="form.fecha_inicio_laboral" type="date" />
            </div>
            <div class="campo">
              <label>Fecha fin laboral</label>
              <input v-model="form.fecha_fin_laboral" type="date" />
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
            <button @click="modoFoto = 'camara'" :class="['btn-opcion', modoFoto === 'camara' ? 'activo' : '']">
              Usar cámara
            </button>
            <button @click="modoFoto = 'archivo'" :class="['btn-opcion', modoFoto === 'archivo' ? 'activo' : '']">
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
            <input type="file" accept="image/*" multiple @change="cargarArchivos" ref="inputArchivo"
              style="display:none" />
            <button @click="$refs.inputArchivo.click()" class="btn-cargar">
              Seleccionar 3 imágenes
            </button>
            <p class="hint">Seleccione exactamente 3 imágenes</p>
          </div>
          <!-- PREVIEW FOTOS -->
          <div v-if="fotosCapturadas.length > 0" class="fotos-preview">
            <div v-for="(foto, i) in fotosCapturadas" :key="i" class="foto-preview-item" draggable="true"
              @dragstart="dragStart(i)" @dragover.prevent="dragOver(i)" @dragend="dragEnd"
              :class="{ 'arrastrando': dragIndex === i, 'sobre': sobreIndex === i && dragIndex !== i }">
              <div class="drag-handle" title="Arrastrar para reordenar">⠿</div>
              <img :src="foto" alt="Foto" />
              <span class="foto-label">{{ i === 0 ? '⭐ Perfil' : `Foto ${i + 1}` }}</span>
              <button @click="eliminarFoto(i)" class="btn-eliminar-foto">✕</button>
            </div>
          </div>
          <div v-if="errorModal" class="error">{{ errorModal }}</div>
          <div v-if="procesando" class="procesando">Registrando embedding... por favor espere</div>

          <div class="modal-acciones">
            <button @click="paso = 1" class="btn-cancelar">← Volver</button>
            <button @click="guardarConFotos" :disabled="fotosCapturadas.length !== 3 || procesando" class="btn-guardar">
              {{ procesando ? 'Procesando...' : 'Guardar trabajador' }}
            </button>
          </div>
        </div>

      </div>
    </div>

  </AdminLayout>
</template>

<script setup>
import iconoEditar from '@/assets/icon-lapiz.svg'
import iconBasura from '@/assets/icon-basura.svg'
import iconoLupa from '@/assets/icons/icon-lupa.svg'

import { ref, onMounted, watch, computed } from 'vue'
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
const buscar = ref('')
const trabajadoresOriginal = ref([])
const paginaActual = ref(1)
const porPagina = 6


const form = ref({
  nombres: '', apellido_paterno: '', apellido_materno: '',
  dni: '', telefono: '', cargo: '', fecha_inicio_laboral: '',
  rol: 'TRABAJADOR'
})


// Drag & drop para reordenar fotos
const dragIndex = ref(null)
const sobreIndex = ref(null)

function dragStart(i) {
  dragIndex.value = i
}

function dragOver(i) {
  if (dragIndex.value === null || dragIndex.value === i) return
  sobreIndex.value = i

  // Reordena en tiempo real
  const arr = [...fotosCapturadas.value]
  const [item] = arr.splice(dragIndex.value, 1)
  arr.splice(i, 0, item)
  fotosCapturadas.value = arr
  dragIndex.value = i
}

function dragEnd() {
  dragIndex.value = null
  sobreIndex.value = null
}


onMounted(async () => {
  await cargarTrabajadores()
})

async function cargarTrabajadores() {
  cargando.value = true
  try {
    const response = await api.get('/api/trabajadores/')
    trabajadores.value = response.data
    trabajadoresOriginal.value = response.data
  } catch (e) {
    console.error('Error:', e)
  } finally {
    cargando.value = false
  }
}

function buscarTrabajadores() {
  paginaActual.value = 1
  const texto = buscar.value.toLowerCase()

  trabajadores.value = trabajadoresOriginal.value.filter(t =>
    t.dni.includes(texto) ||
    t.nombres.toLowerCase().includes(texto) ||
    t.apellido_paterno.toLowerCase().includes(texto) ||
    t.apellido_materno.toLowerCase().includes(texto)
  )
}

const trabajadoresPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * porPagina
  const fin = inicio + porPagina
  return trabajadores.value.slice(inicio, fin)
})

const totalPaginas = computed(() => {
  return Math.ceil(trabajadores.value.length / porPagina)
})

const paginasVisibles = computed(() => {
  const total = totalPaginas.value
  const actual = paginaActual.value

  let inicio = actual
  let fin = actual + 2

  if (fin > total) {
    fin = total
    inicio = Math.max(1, total - 2)
  }

  const paginas = []
  for (let i = inicio; i <= fin; i++) {
    paginas.push(i)
  }

  return paginas
})

function abrirModalCrear() {
  modoEdicion.value = false
  paso.value = 1
  fotosCapturadas.value = []
  errorModal.value = ''
  form.value = {
    nombres: '', apellido_paterno: '', apellido_materno: '',
    dni: '', telefono: '', cargo: '', fecha_inicio_laboral: '', fecha_fin_laboral: '',
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
    fecha_fin_laboral: t.fecha_fin_laboral?.split('T')[0] || '',

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
  if (!form.value.nombres || !form.value.apellido_paterno || !form.value.dni || !form.value.cargo || !form.value.fecha_inicio_laboral || !form.value.fecha_fin_laboral) {
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
      fecha_fin_laboral: form.value.fecha_fin_laboral,
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


<style scoped src="./style.css"></style>