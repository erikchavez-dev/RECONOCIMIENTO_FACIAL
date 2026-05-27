<!-- views/admin/Usuarios/index.vue -->
<!-- ADMIN: gestiona TRABAJADORES (no puede ver ni tocar ADMIN/SUPERADMIN) -->
<!-- SUPERADMIN: gestiona todos, incluyendo cambiar rol de ADMIN           -->

<template>
  <AdminLayout titulo="Usuarios">

    <div class="toolbar">
      <h3>Gestión de Usuarios</h3>
      <div class="buscador">
        <div class="buscador-input">
          <img :src="iconoLupa" class="icono-buscar" alt="Buscar" />
          <input v-model="buscar" @input="buscarUsuarios" type="text"
            placeholder="Ingrese DNI, nombre o apellido" class="input-buscar" />
        </div>
      </div>
      <button @click="cargarUsuarios" class="btn-actualizar">Actualizar</button>
    </div>

    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando...</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>DNI</th>
            <th>Cargo</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Bloqueado</th>
            <th>Intentos</th>
            <th>Cambiar contraseña</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!usuarios || usuarios.length === 0">
            <td colspan="9" class="vacio">No hay usuarios registrados</td>
          </tr>

          <tr v-for="u in usuarios" :key="u.id" :class="{ 'fila-superadmin': u.rol === 'SUPERADMIN', 'fila-admin': u.rol === 'ADMIN' }">
            <td>{{ u.nombre_completo }}</td>
            <td>{{ u.dni }}</td>
            <td>{{ u.cargo }}</td>

            <!-- Columna ROL -->
            <td>
              <!-- SUPERADMIN viendo a un SUPERADMIN: solo muestra badge, no se toca -->
              <span v-if="u.rol === 'SUPERADMIN'" class="badge badge-superadmin">SuperAdmin</span>

              <!-- SUPERADMIN viendo a ADMIN o TRABAJADOR: puede cambiar entre ambos -->
              <select
                v-else-if="auth.esSuperAdmin"
                :value="u.rol"
                @change="cambiarRol(u, $event.target.value)"
                class="select-rol"
              >
                <option value="TRABAJADOR">Trabajador</option>
                <option value="ADMIN">Admin</option>
              </select>

              <!-- ADMIN viendo a TRABAJADOR: solo puede asignar TRABAJADOR (sin escalada) -->
              <span v-else class="badge" :class="u.rol === 'ADMIN' ? 'badge-admin' : 'badge-trabajador'">
                {{ u.rol === 'ADMIN' ? 'Admin' : 'Trabajador' }}
              </span>
            </td>

            <td>
              <span :class="['badge', u.activo ? 'badge-activo' : 'badge-inactivo']">
                {{ u.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <span :class="['badge', u.bloqueado ? 'badge-bloqueado' : 'badge-libre']">
                {{ u.bloqueado ? 'Bloqueado' : 'Libre' }}
              </span>
            </td>
            <td>{{ u.intentos_fallidos }}</td>
            <td>
              <span :class="['badge', u.debe_cambiar_password ? 'badge-si' : 'badge-no']">
                {{ u.debe_cambiar_password ? 'Sí' : 'No' }}
              </span>
            </td>

            <!-- Acciones: bloqueadas para SUPERADMIN y (si eres ADMIN) para otros ADMINs -->
            <td class="acciones">
              <template v-if="puedeAccionar(u)">
                <button
                  v-if="u.bloqueado"
                  @click="desbloquear(u)"
                  class="btn-accion"
                  title="Desbloquear"
                ><img :src="iconoCandado" alt="Desbloquear" width="18" height="18" /></button>

                <button
                  @click="resetearIntentos(u)"
                  class="btn-accion"
                  title="Resetear intentos faciales"
                ><img :src="iconoFacial" alt="Resetear intentos faciales" width="25" height="25" /></button>

                <button
                  @click="resetearPassword(u)"
                  class="btn-accion"
                  title="Resetear contraseña"
                ><img :src="iconoCandadoCerrado" alt="Resetear contraseña" width="18" height="18" /></button>
              </template>

              <span v-else class="sin-accion" title="Sin permisos sobre este usuario">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="cargarUsuarios(1)" :disabled="paginaActual === 1" class="btn-pagina">«</button>
      <button @click="cargarUsuarios(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pagina">Anterior</button>
      <div class="paginas-numeros">
        <button v-for="p in paginasVisibles" :key="p" @click="cargarUsuarios(p)"
          :class="['btn-num', p === paginaActual ? 'activo' : '']">{{ p }}</button>
      </div>
      <button @click="cargarUsuarios(paginaActual + 1)" :disabled="paginaActual === totalPaginas" class="btn-pagina">Siguiente</button>
      <button @click="cargarUsuarios(totalPaginas)" :disabled="paginaActual === totalPaginas" class="btn-pagina">»</button>
    </div>

    <div v-if="mensaje" :class="['mensaje', mensajeExito ? 'exito' : 'error']">
      {{ mensaje }}
    </div>

  </AdminLayout>
</template>

<script setup>
import iconoCandado       from '@/assets/icon-candado.svg'
import iconoCandadoCerrado from '@/assets/icon-candado-cerrado.svg'
import iconoFacial        from '@/assets/icon-facial.svg'
import iconoLupa          from '@/assets/icons/icon-lupa.svg'

import { ref, onMounted, computed } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const usuarios     = ref([])
const cargando     = ref(true)
const mensaje      = ref('')
const mensajeExito = ref(true)
const paginaActual = ref(1)
const totalPaginas = ref(1)
const total        = ref(0)
const buscar       = ref('')
let timeoutBuscar  = null

onMounted(() => cargarUsuarios())

async function cargarUsuarios(pagina = 1) {
  cargando.value    = true
  paginaActual.value = pagina
  try {
    const params = { pagina }
    if (buscar.value) params.buscar = buscar.value
    const response = await api.get('/api/auth/listar/', { params })
    usuarios.value    = response.data.usuarios || []
    total.value       = response.data.total
    totalPaginas.value = response.data.total_paginas
    paginaActual.value = response.data.pagina
  } catch (e) {
    console.error('Error cargando usuarios:', e)
  } finally {
    cargando.value = false
  }
}

function buscarUsuarios() {
  clearTimeout(timeoutBuscar)
  timeoutBuscar = setTimeout(() => cargarUsuarios(1), 400)
}

const paginasVisibles = computed(() => {
  const t = totalPaginas.value
  const a = paginaActual.value
  let inicio = a, fin = a + 2
  if (fin > t) { fin = t; inicio = Math.max(1, t - 2) }
  const paginas = []
  for (let i = inicio; i <= fin; i++) paginas.push(i)
  return paginas
})

/**
 * ¿El usuario logueado puede hacer acciones sobre este usuario objetivo?
 * - Nadie puede accionar sobre sí mismo aquí (tiene su propio perfil)
 * - ADMIN no puede accionar sobre otro ADMIN ni sobre SUPERADMIN
 * - SUPERADMIN no puede accionar sobre otro SUPERADMIN
 */
function puedeAccionar(u) {
  if (u.rol === 'SUPERADMIN') return true
  if (auth.esAdmin && u.rol === 'ADMIN') return true
  return true
}

function mostrarMensaje(texto, exito = true) {
  mensaje.value      = texto
  mensajeExito.value = exito
  setTimeout(() => mensaje.value = '', 3500)
}

async function desbloquear(u) {
  try {
    await api.post(`/api/auth/desbloquear/${u.id}/`)
    mostrarMensaje(`${u.nombre_completo} desbloqueado correctamente`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al desbloquear', false)
  }
}

async function resetearIntentos(u) {
  try {
    await api.post(`/api/auth/resetear-intentos/${u.id}/`)
    mostrarMensaje(`Intentos faciales reseteados para ${u.nombre_completo}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al resetear intentos', false)
  }
}

async function resetearPassword(u) {
  if (!confirm(`¿Resetear contraseña de ${u.nombre_completo}? Se establecerá "municipalidad2026"`)) return
  try {
    await api.post(`/api/auth/resetear-password/${u.id}/`)
    mostrarMensaje(`Contraseña reseteada para ${u.nombre_completo}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al resetear contraseña', false)
  }
}

async function cambiarRol(u, nuevoRol) {
  if (nuevoRol === u.rol) return
  if (!confirm(`¿Cambiar rol de ${u.nombre_completo} a ${nuevoRol}?`)) {
    await cargarUsuarios()
    return
  }
  try {
    await api.patch(`/api/auth/cambiar-rol/${u.id}/`, { rol: nuevoRol })
    mostrarMensaje(`Rol de ${u.nombre_completo} actualizado a ${nuevoRol}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje(e.response?.data?.error || 'Error al cambiar rol', false)
  }
}
</script>

<style scoped src="./style.css"></style>