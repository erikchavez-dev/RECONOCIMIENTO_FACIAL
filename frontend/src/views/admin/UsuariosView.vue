<!-- UsuariosView.vue — Gestión de usuarios del sistema -->
<!-- Ver lista, desbloquear, resetear intentos, resetear contraseña, cambiar rol -->

<template>
  <AdminLayout titulo="Usuarios">

  <!-- BUSCADOR -->
    <div class="buscador">
      <input v-model="buscar" @input="buscarTrabajadores" type="text" placeholder="Buscar por DNI, nombre o apellido..."
        class="input-buscar" />
    </div>

    <div class="toolbar">
      <h3>Gestión de Usuarios</h3>
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
            <th>Bloqueado</th>
            <th>Intentos</th>
            <th>Cambiar contraseña</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="usuarios.length === 0">
            <td colspan="9" class="vacio">No hay usuarios registrados</td>
          </tr>
          <tr v-for="u in usuarios" :key="u.id">
            <td>{{ u.nombre_completo }}</td>
            <td>{{ u.dni }}</td>
            <td>{{ u.cargo }}</td>
            <td>
              <select
                :value="u.rol"
                @change="cambiarRol(u, $event.target.value)"
                class="select-rol"
              >
                <option value="TRABAJADOR">Trabajador</option>
                <option value="ADMIN">Admin</option>
              </select>
            </td>
            <td>
             <span
                :class="['badge', u.bloqueado === true || u.bloqueado === 'true' ? 'badge-bloqueado' : 'badge-libre']">
                {{ u.bloqueado === true || u.bloqueado === 'true' ? 'Bloqueado' : 'Libre' }}
              </span>
            </td>
            <td>{{ u.intentos_fallidos }}</td>
            <td>
              <span :class="['badge', u.debe_cambiar_password ? 'badge-si' : 'badge-no']">
                {{ u.debe_cambiar_password ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="acciones">
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
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  <!-- PAGINACIÓN -->
    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="cambiarPagina(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pagina">←
        Anterior</button>

      <span class="pagina-info">
        Página {{ paginaActual }} de {{ totalPaginas }} ({{ total }} registros)
      </span>

      <button @click="cambiarPagina(paginaActual + 1)" :disabled="paginaActual === totalPaginas"
        class="btn-pagina">Siguiente →</button>
    </div>
    <!-- MENSAJE -->
    <div v-if="mensaje" :class="['mensaje', mensajeExito ? 'exito' : 'error']">
      {{ mensaje }}
    </div>

  </AdminLayout>
</template>

<script setup>
import iconoCandado from '@/assets/icon-candado.svg'
import iconoCandadoCerrado from '@/assets/icon-candado-cerrado.svg'
import iconoFacial from '@/assets/icon-facial.svg'

import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const usuarios = ref([])
const cargando = ref(true)
const mensaje = ref('')
const mensajeExito = ref(true)

// Paginación y búsqueda
const buscar = ref('')
const paginaActual = ref(1)
const totalPaginas = ref(1)
const total = ref(0)
let timeoutBuscar = null

onMounted(async () => {
  await cargarUsuarios()
})

async function cargarUsuarios() {
  cargando.value = true
  try {
    const params = new URLSearchParams({ pagina: paginaActual.value })
    if (buscar.value) params.append('buscar', buscar.value)

    const response = await api.get(`/api/auth/listar/?${params}`)
    usuarios.value = response.data.usuarios
    total.value = response.data.total
    totalPaginas.value = response.data.total_paginas
  } catch (e) {
    console.error('Error cargando usuarios:', e)
  } finally {
    cargando.value = false
  }
}

function buscarTrabajadores() {
  clearTimeout(timeoutBuscar)
  timeoutBuscar = setTimeout(() => {
    paginaActual.value = 1
    cargarUsuarios()
  }, 400)
}

function cambiarPagina(pagina) {
  if (pagina < 1 || pagina > totalPaginas.value) return
  paginaActual.value = pagina
  cargarUsuarios()
}

function mostrarMensaje(texto, exito = true) {
  mensaje.value = texto
  mensajeExito.value = exito
  setTimeout(() => mensaje.value = '', 3000)
}

async function desbloquear(u) {
  try {
    await api.post(`/api/auth/desbloquear/${u.id}/`)
    mostrarMensaje(`Usuario ${u.nombre_completo} desbloqueado correctamente`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje('Error al desbloquear usuario', false)
  }
}

async function resetearIntentos(u) {
  try {
    await api.post(`/api/auth/resetear-intentos/${u.id}/`)
    mostrarMensaje(`Intentos faciales reseteados para ${u.nombre_completo}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje('Error al resetear intentos', false)
  }
}

async function resetearPassword(u) {
  if (!confirm(`¿Resetear contraseña de ${u.nombre_completo}? Se establecerá "municipalidad2026"`)) return
  try {
    await api.post(`/api/auth/resetear-password/${u.id}/`)
    mostrarMensaje(`Contraseña reseteada para ${u.nombre_completo}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje('Error al resetear contraseña', false)
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
    mostrarMensaje(`Rol actualizado a ${nuevoRol}`)
    await cargarUsuarios()
  } catch (e) {
    mostrarMensaje('Error al cambiar rol', false)
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

.btn-actualizar {
  background: #1a3a6b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-actualizar:hover { background: #142d54; }

.tabla-container {
  background: white;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.85rem; }

.tabla th {
  background: #1a3a6b;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}

.tabla td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.tabla tr:hover { background: #f8fafc; }

.select-rol {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.82rem;
  cursor: pointer;
}

.select-rol:focus { outline: none; border-color: #1a3a6b; }

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}

.badge-activo { background: #dcfce7; color: #16a34a; }
.badge-inactivo { background: #fee2e2; color: #dc2626; }
.badge-bloqueado { background: #fee2e2; color: #dc2626; }
.badge-libre { background: #dcfce7; color: #16a34a; }
.badge-si { background: #fef9c3; color: #ca8a04; }
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

.cargando, .vacio {
  text-align: center;
  padding: 40px;
  color: #666;
}

.mensaje {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.88rem;
  text-align: center;
}

.exito { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }


/* BUSCADOR */
.buscador {
  margin-bottom: 16px;
}

.input-buscar {
  width: 100%;
  max-width: 400px;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
}

.input-buscar:focus {
  border-color: #1a3a6b;
}

/* PAGINACIÓN */
.paginacion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
}

.btn-pagina {
  padding: 8px 16px;
  background: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.88rem;
}

.btn-pagina:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.pagina-info {
  font-size: 0.88rem;
  color: #555;
}


</style>