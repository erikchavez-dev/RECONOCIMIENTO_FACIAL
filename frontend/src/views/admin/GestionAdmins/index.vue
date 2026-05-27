<!-- views/admin/GestionAdmins/index.vue -->
<!-- Exclusivo SUPERADMIN: promover TRABAJADORES a ADMIN y degradar ADMINs -->

<template>
  <AdminLayout titulo="Gestión de Admins">

    <!-- ADMINS ACTUALES -->
    <section class="seccion">
      <h4 class="seccion-titulo">Administradores actuales</h4>
      <div v-if="cargandoAdmins" class="cargando">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>DNI</th>
            <th>Cargo</th>
            <th>Bloqueado</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="admins.length === 0">
            <td colspan="5" class="vacio">No hay administradores registrados</td>
          </tr>
          <tr v-for="u in admins" :key="u.id">
            <td>{{ u.nombre_completo }}</td>
            <td>{{ u.dni }}</td>
            <td>{{ u.cargo }}</td>
            <td>
              <span :class="['badge', u.bloqueado ? 'badge-bloqueado' : 'badge-libre']">
                {{ u.bloqueado ? 'Bloqueado' : 'Libre' }}
              </span>
            </td>
            <td>
              <button @click="degradar(u)" class="btn-degradar" title="Degradar a Trabajador">
                Quitar Admin
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- PROMOVER TRABAJADOR -->
    <section class="seccion">
      <h4 class="seccion-titulo">Promover trabajador a Admin</h4>
      <div class="buscador-input">
        <input v-model="buscar" @input="buscarTrabajadores" type="text"
          placeholder="Buscar por DNI, nombre o apellido" class="input-buscar" />
      </div>

      <div v-if="cargandoTrabajadores" class="cargando">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>DNI</th>
            <th>Cargo</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="trabajadores.length === 0">
            <td colspan="4" class="vacio">No hay trabajadores disponibles</td>
          </tr>
          <tr v-for="u in trabajadores" :key="u.id">
            <td>{{ u.nombre_completo }}</td>
            <td>{{ u.dni }}</td>
            <td>{{ u.cargo }}</td>
            <td>
              <button @click="promover(u)" class="btn-promover" title="Promover a Admin">
                Hacer Admin
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-if="mensaje" :class="['mensaje', mensajeExito ? 'exito' : 'error']">
      {{ mensaje }}
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const admins              = ref([])
const trabajadores        = ref([])
const cargandoAdmins      = ref(true)
const cargandoTrabajadores = ref(true)
const mensaje             = ref('')
const mensajeExito        = ref(true)
const buscar              = ref('')
let timeoutBuscar         = null

onMounted(() => {
  cargarAdmins()
  cargarTrabajadores()
})

async function cargarAdmins() {
  cargandoAdmins.value = true
  try {
    // Pide todos los usuarios y filtra ADMIN del lado cliente
    // (el backend ya filtra según el rol del que consulta)
    const res = await api.get('/api/auth/listar/', { params: { limite: 100 } })
    admins.value = (res.data.usuarios || []).filter(u => u.rol === 'ADMIN')
  } catch (e) {
    console.error(e)
  } finally {
    cargandoAdmins.value = false
  }
}

async function cargarTrabajadores(texto = '') {
  cargandoTrabajadores.value = true
  try {
    const params = { limite: 8 }
    if (texto) params.buscar = texto
    const res = await api.get('/api/auth/listar/', { params })
    trabajadores.value = (res.data.usuarios || []).filter(u => u.rol === 'TRABAJADOR')
  } catch (e) {
    console.error(e)
  } finally {
    cargandoTrabajadores.value = false
  }
}

function buscarTrabajadores() {
  clearTimeout(timeoutBuscar)
  timeoutBuscar = setTimeout(() => cargarTrabajadores(buscar.value), 400)
}

function mostrarMensaje(texto, exito = true) {
  mensaje.value      = texto
  mensajeExito.value = exito
  setTimeout(() => mensaje.value = '', 3500)
}

async function promover(u) {
  if (!confirm(`¿Promover a ${u.nombre_completo} como Administrador?`)) return
  try {
    await api.post('/api/auth/gestion-admin/', { usuario_id: u.id })
    mostrarMensaje(`${u.nombre_completo} ahora es ADMIN`)
    await Promise.all([cargarAdmins(), cargarTrabajadores(buscar.value)])
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al promover', false)
  }
}

async function degradar(u) {
  if (!confirm(`¿Quitar permisos de Admin a ${u.nombre_completo}? Pasará a ser Trabajador.`)) return
  try {
    await api.delete(`/api/auth/gestion-admin/${u.id}/`)
    mostrarMensaje(`${u.nombre_completo} degradado a Trabajador`)
    await Promise.all([cargarAdmins(), cargarTrabajadores(buscar.value)])
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al degradar', false)
  }
}
</script>

<style scoped src="./style.css"></style>