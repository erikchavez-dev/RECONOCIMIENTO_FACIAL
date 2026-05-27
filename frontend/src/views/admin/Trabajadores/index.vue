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
              <img :src="t.foto_url ? `${API_URL}${t.foto_url}` : '/sin-foto.png'" class="foto-trabajador" alt="Foto" />
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
              <!-- BOTÓN EDITAR: ADMIN y SUPERADMIN -->
              <button @click="abrirModalEditar(t)" class="btn-accion" title="Editar">
                <img :src="iconoEditar" alt="Editar" width="22" height="22" />
              </button>

              <!-- BOTÓN ACTUALIZAR EMBEDDING: solo SUPERADMIN -->
              <button
                v-if="auth.esSuperAdmin"
                @click="abrirModalEmbedding(t)"
                class="btn-accion"
                title="Actualizar rostro"
              >
                <img :src="iconoFacial" alt="Rostro" width="22" height="22" />
              </button>
              <span
                v-else
                class="btn-accion-disabled"
                title="Solo el SuperAdmin puede actualizar el rostro"
              >
                <img :src="iconoFacial" alt="Rostro" width="22" height="22" style="opacity:0.3; display: none;" />
              </span>

              <!-- INTERRUPTOR: deshabilitado si contrato vencido -->
              <label class="switch-button" :title="contratoVencido(t) ? 'Contrato vencido — no se puede activar' : ''">
                <input type="checkbox" :checked="t.activo" :disabled="contratoVencido(t)" @change="toggleActivo(t)">
                <span class="slider-round" :class="{ 'slider-disabled': contratoVencido(t) }"></span>
              </label>

              <!-- BOTÓN ELIMINAR -->
               <button
               v-if="auth.esSuperAdmin"
               @click="eliminar(t)"
               class="btn-accion-delete"
               title="Eliminar"
               >
               <img :src="iconBasura" alt="Eliminar" width="18" height="18" />
               </button>
               <span
               v-else
               class="btn-accion-disabled"
               title="Solo el SuperAdmin puede eliminar trabajadores"
               >
               <img :src="iconBasura" alt="Eliminar" width="18" height="18" style="opacity:0.3; display: none;" />
               </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="paginaActual = 1" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">«</button>
      <button @click="paginaActual--" :disabled="paginaActual === 1" class="btn-pagina">‹ Anterior</button>
      <div class="paginas-numeros">
        <button v-for="p in paginasVisibles" :key="p" @click="paginaActual = p"
          :class="['btn-num', p === paginaActual ? 'activo' : '']">{{ p }}</button>
      </div>
      <button @click="paginaActual++" :disabled="paginaActual === totalPaginas" class="btn-pagina">Siguiente ›</button>
      <button @click="paginaActual = totalPaginas" :disabled="paginaActual === totalPaginas" class="btn-pagina btn-extremo">»</button>
    </div>

    <!-- MODAL CREAR/EDITAR -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <h3>{{ modoEdicion ? 'Editar Trabajador' : 'Nuevo Trabajador' }}</h3>


       <!-- PASO 1: DATOS -->
        <div v-if="paso === 1">
          <div class="form-grid">

            <div class="campo">
              <label>Nombres <span class="req">*</span></label>
              <input v-model="form.nombres" type="text" placeholder="Nombres" @keydown="soloLetras($event)"
                @input="limpiarLetras('nombres')" :class="{ 'input-error': erroresCampo.nombres }" autocomplete="off" />
              <span v-if="erroresCampo.nombres" class="campo-error">{{ erroresCampo.nombres }}</span>
            </div>

            <div class="campo">
              <label>Apellido Paterno <span class="req">*</span></label>
              <input v-model="form.apellido_paterno" type="text" placeholder="Apellido Paterno"
                @keydown="soloLetras($event)" @input="limpiarLetras('apellido_paterno')"
                :class="{ 'input-error': erroresCampo.apellido_paterno }" autocomplete="off" />
              <span v-if="erroresCampo.apellido_paterno" class="campo-error">{{ erroresCampo.apellido_paterno }}</span>
            </div>

            <div class="campo">
              <label>Apellido Materno <span class="req">*</span></label>
              <input v-model="form.apellido_materno" type="text" placeholder="Apellido Materno"
                @keydown="soloLetras($event)" @input="limpiarLetras('apellido_materno')"
                :class="{ 'input-error': erroresCampo.apellido_materno }" autocomplete="off" />
              <span v-if="erroresCampo.apellido_materno" class="campo-error">{{ erroresCampo.apellido_materno }}</span>
            </div>

            <div class="campo">
              <label>DNI <span class="req">*</span></label>
              <input v-model="form.dni" type="text" maxlength="8" placeholder="DNI (8 dígitos)"
                @keydown="soloNumeros($event)" @input="limpiarNumeros('dni', 8)" :disabled="modoEdicion"
                :class="{ 'input-error': erroresCampo.dni }" autocomplete="off" />
              <span v-if="erroresCampo.dni" class="campo-error">{{ erroresCampo.dni }}</span>
            </div>

            <div class="campo">
              <label>Teléfono <span class="req">*</span></label>
              <input v-model="form.telefono" type="text" maxlength="9" placeholder="Teléfono (9 dígitos)"
                @keydown="soloNumeros($event)" @input="limpiarNumeros('telefono', 9)"
                :class="{ 'input-error': erroresCampo.telefono }" autocomplete="off" />
              <span v-if="erroresCampo.telefono" class="campo-error">{{ erroresCampo.telefono }}</span>
            </div>

            <div class="campo">
              <label>Cargo <span class="req">*</span></label>
              <input v-model="form.cargo" type="text" placeholder="Cargo"
              @keydown="soloLetras($event)" @input="limpiarCargo('cargo')"
              :class="{ 'input-error': erroresCampo.cargo }" autocomplete="off" />
              <span v-if="erroresCampo.cargo" class="campo-error">{{ erroresCampo.cargo }}</span>
            </div>

            <div class="campo">
              <label>Fecha inicio laboral <span class="req">*</span></label>
              <input v-model="form.fecha_inicio_laboral" type="date"
                :class="{ 'input-error': erroresCampo.fecha_inicio_laboral }" />
              <span v-if="erroresCampo.fecha_inicio_laboral" class="campo-error">{{ erroresCampo.fecha_inicio_laboral
                }}</span>
            </div>

          <div class="campo">
              <label>Fecha fin laboral</label>
              <input v-model="form.fecha_fin_laboral" type="date" :disabled="form.contrato_indefinido"
                :class="{ 'input-disabled': form.contrato_indefinido }" />
              <div class="check-indefinido">
                <input type="checkbox" id="indefinido" v-model="form.contrato_indefinido" />
                <label for="indefinido">
                  Contrato indefinido
                </label>
              </div>
              <span v-if="erroresCampo.fecha_fin_laboral" class="campo-error">
                {{ erroresCampo.fecha_fin_laboral }}
              </span>
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
          <div class="opciones-foto">
            <button @click="modoFoto = 'camara'" :class="['btn-opcion', modoFoto === 'camara' ? 'activo' : '']">Usar cámara</button>
            <button @click="modoFoto = 'archivo'" :class="['btn-opcion', modoFoto === 'archivo' ? 'activo' : '']">Cargar imágenes</button>
          </div>
          <div v-if="modoFoto === 'camara'" class="camara-section">
            <div class="camara-wrapper">
              <video ref="videoRef" autoplay playsinline class="video"></video>
              <canvas ref="canvasRef" style="display:none"></canvas>
            </div>
            <button @click="capturarFoto" :disabled="fotosCapturadas.length >= 3" class="btn-capturar">
              Capturar foto ({{ fotosCapturadas.length }}/3)
            </button>
          </div>
          <div v-if="modoFoto === 'archivo'" class="archivo-section">
            <input type="file" accept="image/*" multiple @change="cargarArchivos" ref="inputArchivo" style="display:none" />
            <button @click="$refs.inputArchivo.click()" class="btn-cargar">Seleccionar 3 imágenes</button>
            <p class="hint">Seleccione exactamente 3 imágenes</p>
          </div>
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

    <!-- MODAL ACTUALIZAR EMBEDDING (solo SUPERADMIN) -->
    <div v-if="mostrarModalEmbedding" class="modal-overlay" @click.self="cerrarModalEmbedding">
      <div class="modal">
        <h3>Actualizar rostro — {{ trabajadorEmbedding?.nombres }} {{ trabajadorEmbedding?.apellido_paterno }}</h3>
        <p class="instruccion-fotos">Capture o cargue <strong>3 fotos</strong> actualizadas del trabajador.</p>
        <div class="opciones-foto">
          <button @click="modoFotoEmb = 'camara'" :class="['btn-opcion', modoFotoEmb === 'camara' ? 'activo' : '']">Usar cámara</button>
          <button @click="modoFotoEmb = 'archivo'" :class="['btn-opcion', modoFotoEmb === 'archivo' ? 'activo' : '']">Cargar imágenes</button>
        </div>
        <div v-if="modoFotoEmb === 'camara'" class="camara-section">
          <div class="camara-wrapper">
            <video ref="videoEmbRef" autoplay playsinline class="video"></video>
            <canvas ref="canvasEmbRef" style="display:none"></canvas>
          </div>
          <button @click="capturarFotoEmb" :disabled="fotosEmb.length >= 3" class="btn-capturar">
            Capturar foto ({{ fotosEmb.length }}/3)
          </button>
        </div>
        <div v-if="modoFotoEmb === 'archivo'" class="archivo-section">
          <input type="file" accept="image/*" multiple @change="cargarArchivosEmb" ref="inputArchivoEmb" style="display:none" />
          <button @click="$refs.inputArchivoEmb.click()" class="btn-cargar">Seleccionar 3 imágenes</button>
          <p class="hint">Seleccione exactamente 3 imágenes</p>
        </div>
        <div v-if="fotosEmb.length > 0" class="fotos-preview">
          <div v-for="(foto, i) in fotosEmb" :key="i" class="foto-preview-item" draggable="true"
            @dragstart="dragStartEmb(i)" @dragover.prevent="dragOverEmb(i)" @dragend="dragEndEmb" :class="{
              'arrastrando': dragIndexEmb === i,
              'sobre': sobreIndexEmb === i && dragIndexEmb !== i
            }">
            <div class="drag-handle" title="Arrastrar para reordenar">⠿</div>

            <img :src="foto" alt="Foto" />

            <span class="foto-label">
              {{ i === 0 ? '⭐ Perfil' : `Foto ${i + 1}` }}
            </span>

            <button @click="fotosEmb.splice(i, 1)" class="btn-eliminar-foto">
              ✕
            </button>
          </div>
        </div>
        <div v-if="errorEmb" class="error">{{ errorEmb }}</div>
        <div v-if="procesandoEmb" class="procesando">Actualizando embedding... por favor espere</div>
        <div class="modal-acciones">
          <button @click="cerrarModalEmbedding" class="btn-cancelar">Cancelar</button>
          <button @click="guardarEmbedding" :disabled="fotosEmb.length !== 3 || procesandoEmb" class="btn-guardar">
            {{ procesandoEmb ? 'Procesando...' : 'Actualizar rostro' }}
          </button>
        </div>
      </div>
    </div>

  </AdminLayout>
</template>

<script setup>
import iconoEditar from '@/assets/icon-lapiz.svg'
import iconBasura  from '@/assets/icon-basura.svg'
import iconoLupa   from '@/assets/icons/icon-lupa.svg'
import iconoFacial from '@/assets/icons/revert-face.png'

import { ref, onMounted, watch, computed } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth    = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL

const trabajadores         = ref([])
const cargando             = ref(true)
const mostrarModal         = ref(false)
const modoEdicion          = ref(false)
const guardando            = ref(false)
const procesando           = ref(false)
const errorModal           = ref('')
const trabajadorSeleccionado = ref(null)
const paso                 = ref(1)
const modoFoto             = ref('camara')
const fotosCapturadas      = ref([])
const videoRef             = ref(null)
const canvasRef            = ref(null)
const inputArchivo         = ref(null)
let stream                 = null
const buscar               = ref('')
const trabajadoresOriginal = ref([])
const paginaActual         = ref(1)
const porPagina            = 6

// ── Modal embedding ─────────────────────────────────────────────────────────
const mostrarModalEmbedding  = ref(false)
const trabajadorEmbedding    = ref(null)
const fotosEmb               = ref([])
const modoFotoEmb            = ref('camara')
const errorEmb               = ref('')
const procesandoEmb          = ref(false)
const videoEmbRef            = ref(null)
const canvasEmbRef           = ref(null)
let streamEmb                = null

// Drag & drop
const dragIndex  = ref(null)
const sobreIndex = ref(null)
const dragIndexEmb = ref(null)
const sobreIndexEmb = ref(null)

function dragStart(i) { dragIndex.value = i }
function dragOver(i) {
  if (dragIndex.value === null || dragIndex.value === i) return
  sobreIndex.value = i
  const arr  = [...fotosCapturadas.value]
  const [item] = arr.splice(dragIndex.value, 1)
  arr.splice(i, 0, item)
  fotosCapturadas.value = arr
  dragIndex.value = i
}
function dragEnd() { dragIndex.value = null; sobreIndex.value = null }

function dragStartEmb(i) {
  dragIndexEmb.value = i
}

function dragOverEmb(i) {
  if (dragIndexEmb.value === null || dragIndexEmb.value === i) return

  sobreIndexEmb.value = i

  const arr = [...fotosEmb.value]

  const [item] = arr.splice(dragIndexEmb.value, 1)

  arr.splice(i, 0, item)

  fotosEmb.value = arr

  dragIndexEmb.value = i
}

function dragEndEmb() {
  dragIndexEmb.value = null
  sobreIndexEmb.value = null
}

onMounted(() => cargarTrabajadores())

async function cargarTrabajadores() {
  cargando.value = true
  try {
    const response = await api.get('/api/trabajadores/')
    trabajadores.value         = response.data
    trabajadoresOriginal.value = response.data
  } catch (e) { console.error('Error:', e) }
  finally { cargando.value = false }
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
  return trabajadores.value.slice(inicio, inicio + porPagina)
})

const totalPaginas = computed(() => Math.ceil(trabajadores.value.length / porPagina))

const paginasVisibles = computed(() => {
  const total = totalPaginas.value, actual = paginaActual.value
  let inicio = actual, fin = actual + 2
  if (fin > total) { fin = total; inicio = Math.max(1, total - 2) }
  const paginas = []
  for (let i = inicio; i <= fin; i++) paginas.push(i)
  return paginas
})

// ── Modal crear/editar ───────────────────────────────────────────────────────

const form = ref({
  nombres: '',
  apellido_paterno: '',
  apellido_materno: '',
  dni: '',
  telefono: '',
  cargo: '',
  fecha_inicio_laboral: '',
  fecha_fin_laboral: '',
  contrato_indefinido: false
})
watch(() => form.value.contrato_indefinido, (valor) => {
  if (valor) {
    form.value.fecha_fin_laboral = null
    erroresCampo.value.fecha_fin_laboral = ''
  }
})


const erroresCampo = ref({
  nombres: '',
  apellido_paterno: '',
  apellido_materno: '',
  dni: '',
  telefono: '',
  cargo: '',
  fecha_inicio_laboral: '',
  fecha_fin_laboral: '',
})

function limpiarErrores() {
  Object.keys(erroresCampo.value).forEach(
    k => erroresCampo.value[k] = ''
  )
}

function soloLetras(event) {
  const controlKeys = [
    'Backspace',
    'Delete',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Tab',
    'Home',
    'End',
    'Shift',
    'Control',
    'Alt',
    'Meta',
    'Enter',
  ]

  if (controlKeys.includes(event.key)) return

  if (event.ctrlKey || event.metaKey) return

  const valido = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']$/.test(event.key)

  if (!valido) {
    event.preventDefault()
  }
}

function soloNumeros(event) {
  const controlKeys = [
    'Backspace',
    'Delete',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Tab',
    'Home',
    'End',
    'Shift',
    'Control',
    'Alt',
    'Meta',
    'Enter',
  ]

  if (controlKeys.includes(event.key)) return

  if (event.ctrlKey || event.metaKey) return

  if (!/^\d$/.test(event.key)) {
    event.preventDefault()
  }
}

function limpiarLetras(campo) {
  const val = form.value[campo]

  const limpio = val
    .replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']/g, '')
    .toUpperCase()

  if (val !== limpio) {
    form.value[campo] = limpio
  }

  erroresCampo.value[campo] =
    limpio.trim().length < 2
      ? 'Mínimo 2 caracteres'
      : ''
}

function limpiarNumeros(campo, maxLength) {
  const val = form.value[campo]

  const limpio = val
    .replace(/\D/g, '')
    .slice(0, maxLength)

  if (val !== limpio) {
    form.value[campo] = limpio
  }

  if (campo === 'dni') {
    erroresCampo.value.dni =
      limpio.length > 0 && limpio.length !== 8
        ? `El DNI debe tener 8 dígitos (${limpio.length}/8)`
        : ''
  }

  if (campo === 'telefono') {
    erroresCampo.value.telefono =
      limpio.length > 0 && limpio.length < 7
        ? 'Teléfono muy corto'
        : ''
  }
}

function limpiarCargo(campo) {
  const val = form.value[campo]

  const limpio = val
    .replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-\./()]/g, '')
    .toUpperCase()

  if (val !== limpio) {
    form.value[campo] = limpio
  }

  erroresCampo.value.cargo =
    limpio.trim().length < 2
      ? 'Mínimo 2 caracteres'
      : ''
}

function abrirModalCrear() {
  modoEdicion.value = false
  paso.value = 1
  fotosCapturadas.value = []
  errorModal.value = ''

  form.value = {
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    dni: '',
    telefono: '',
    cargo: '',
    fecha_inicio_laboral: '',
    fecha_fin_laboral: '',
    contrato_indefinido: false
  }

  limpiarErrores()

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
    contrato_indefinido: !t.fecha_fin_laboral,
  }

  limpiarErrores()

  errorModal.value = ''
  mostrarModal.value = true
}
function cerrarModal() {
  detenerCamara()
  mostrarModal.value    = false
  errorModal.value      = ''
  fotosCapturadas.value = []
  paso.value            = 1
}

async function siguientePaso() {

  if (
    !form.value.nombres ||
    !form.value.apellido_paterno ||
    !form.value.dni ||
    !form.value.cargo ||
    !form.value.fecha_inicio_laboral ||
    (
      !form.value.contrato_indefinido &&
      !form.value.fecha_fin_laboral
    )
  ) {
    errorModal.value = 'Complete todos los campos obligatorios'
    return
  }

  errorModal.value = ''
  paso.value = 2

  if (modoFoto.value === 'camara') {
    await iniciarCamara()
  }
}

async function iniciarCamara() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 } })
    if (videoRef.value) videoRef.value.srcObject = stream
  } catch { errorModal.value = 'No se pudo acceder a la cámara'; modoFoto.value = 'archivo' }
}

function detenerCamara() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

function capturarFoto() {
  if (fotosCapturadas.value.length >= 3) return
  const canvas = canvasRef.value, video = videoRef.value
  canvas.width = video.videoWidth; canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  fotosCapturadas.value.push(canvas.toDataURL('image/jpeg', 0.8))
}

function cargarArchivos(event) {
  const files = Array.from(event.target.files)
  if (files.length !== 3) { errorModal.value = 'Debe seleccionar exactamente 3 imágenes'; return }
  errorModal.value = ''; fotosCapturadas.value = []
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => fotosCapturadas.value.push(e.target.result)
    reader.readAsDataURL(file)
  })
}

function eliminarFoto(index) { fotosCapturadas.value.splice(index, 1) }

async function guardar() {
  errorModal.value = ''; guardando.value = true
  try {
    await api.patch(`/api/trabajadores/${trabajadorSeleccionado.value.id}/`, {
      nombres: form.value.nombres,
      apellido_paterno: form.value.apellido_paterno,
      apellido_materno: form.value.apellido_materno,
      telefono: form.value.telefono,
      cargo: form.value.cargo,
      fecha_inicio_laboral: form.value.fecha_inicio_laboral,
      fecha_fin_laboral: form.value.contrato_indefinido
      ? null
      : form.value.fecha_fin_laboral,
    })
    
    cerrarModal()
    await cargarTrabajadores()
  } catch (e) {
    errorModal.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'Error al guardar'
  } finally { guardando.value = false }
}

async function guardarConFotos() {
  if (fotosCapturadas.value.length !== 3) { errorModal.value = 'Se necesitan exactamente 3 fotos'; return }
  errorModal.value = ''; procesando.value = true
  try {
    const response = await api.post('/api/trabajadores/', {
      nombres: form.value.nombres, apellido_paterno: form.value.apellido_paterno,
      apellido_materno: form.value.apellido_materno, dni: form.value.dni,
      telefono: form.value.telefono, cargo: form.value.cargo,
      fecha_inicio_laboral: form.value.fecha_inicio_laboral,
      fecha_fin_laboral: form.value.contrato_indefinido
      ? null
      : form.value.fecha_fin_laboral,
    })
    const trabajador = response.data
    await api.post(`/api/trabajadores/${trabajador.id}/foto/`, { imagen: fotosCapturadas.value[0] })
    await api.post('/api/reconocimiento/registrar-embedding/', { trabajador_id: trabajador.id, imagenes: fotosCapturadas.value })
    detenerCamara(); cerrarModal(); await cargarTrabajadores()
  } catch (e) {
    errorModal.value = e.response?.data?.error || 'Error al procesar las fotos'
  } finally { procesando.value = false }
}

// ── Modal embedding (SUPERADMIN) ─────────────────────────────────────────────
function abrirModalEmbedding(t) {
  trabajadorEmbedding.value  = t
  fotosEmb.value             = []
  errorEmb.value             = ''
  modoFotoEmb.value          = 'camara'
  mostrarModalEmbedding.value = true
  setTimeout(() => iniciarCamaraEmb(), 100)
}

function cerrarModalEmbedding() {
  detenerCamaraEmb()
  mostrarModalEmbedding.value = false
  fotosEmb.value = []; errorEmb.value = ''
}

async function iniciarCamaraEmb() {
  try {
    streamEmb = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 } })
    if (videoEmbRef.value) videoEmbRef.value.srcObject = streamEmb
  } catch { errorEmb.value = 'No se pudo acceder a la cámara'; modoFotoEmb.value = 'archivo' }
}

function detenerCamaraEmb() {
  if (streamEmb) { streamEmb.getTracks().forEach(t => t.stop()); streamEmb = null }
}

function capturarFotoEmb() {
  if (fotosEmb.value.length >= 3) return
  const canvas = canvasEmbRef.value, video = videoEmbRef.value
  canvas.width = video.videoWidth; canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  fotosEmb.value.push(canvas.toDataURL('image/jpeg', 0.8))
}

function cargarArchivosEmb(event) {
  const files = Array.from(event.target.files)
  if (files.length !== 3) { errorEmb.value = 'Debe seleccionar exactamente 3 imágenes'; return }
  errorEmb.value = ''; fotosEmb.value = []
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => fotosEmb.value.push(e.target.result)
    reader.readAsDataURL(file)
  })
}

async function guardarEmbedding() {
  if (fotosEmb.value.length !== 3) return
  errorEmb.value = ''; procesandoEmb.value = true
  try {
    await api.post(`/api/trabajadores/${trabajadorEmbedding.value.id}/foto/`, { imagen: fotosEmb.value[0] })
    await api.post('/api/reconocimiento/registrar-embedding/', { trabajador_id: trabajadorEmbedding.value.id, imagenes: fotosEmb.value })
    cerrarModalEmbedding(); await cargarTrabajadores()
    const t = trabajadores.value.find(t => t.id === trabajadorEmbedding.value.id)
    if (t && t.foto_url) t.foto_url = t.foto_url.split('?')[0] + '?t=' + Date.now()
  } catch (e) {
    errorEmb.value = e.response?.data?.error || 'Error al actualizar el rostro'
  } finally { procesandoEmb.value = false }
}

// ── Estado / activar ─────────────────────────────────────────────────────────
function contratoVencido(t) {
  if (!t.fecha_fin_laboral) return false
  const hoy = new Date(); hoy.setHours(0,0,0,0)
  return new Date(t.fecha_fin_laboral + 'T00:00:00') < hoy
}
function estadoBadgeClass(t) {
  if (contratoVencido(t)) return 'badge-vencido'
  return t.activo_efectivo ? 'badge-activo' : 'badge-inactivo'
}
function estadoBadgeTexto(t) {
  if (contratoVencido(t)) return 'Vencido'
  return t.activo_efectivo ? 'Activo' : 'Inactivo'
}
async function toggleActivo(t) {
  if (contratoVencido(t)) return
  try { await api.patch(`/api/trabajadores/${t.id}/activar-desactivar/`); await cargarTrabajadores() }
  catch { alert('Error al cambiar estado') }
}
async function eliminar(t) {
  if (!confirm(`¿Eliminar a ${t.nombres} ${t.apellido_paterno}?`)) return
  try {
    await api.delete(`/api/trabajadores/${t.id}/`)
    await cargarTrabajadores()
  } catch (e) {
    const data = e.response?.data
    if (data?.tiene_marcaciones) {
      if (!confirm(`El trabajador tiene marcaciones registradas.\n¿Eliminar de todas formas?`)) return
      try { await api.delete(`/api/trabajadores/${t.id}/`, { data: { forzar: true } }); await cargarTrabajadores() }
      catch (e2) { alert(e2.response?.data?.error || 'Error al eliminar') }
    } else { alert(data?.error || 'Error al eliminar') }
  }
}
</script>

<style scoped src="./style.css"></style>