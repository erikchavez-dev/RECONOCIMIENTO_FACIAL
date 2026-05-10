<!-- UsuariosView.vue — Gestión de usuarios del sistema -->
<!-- Ver lista, desbloquear, resetear intentos, resetear contraseña, cambiar rol -->

<template>
  <AdminLayout titulo="Usuarios">

    <div class="toolbar">
      <h3>Gestión de Usuarios</h3>
      <div class="buscador">
        <div class="buscador-input">
          <img :src="iconoLupa" class="icono-buscar" alt="Buscar" />
          <input v-model="buscar" @input="buscarUsuarios" type="text"
          placeholder="Buscar por DNI, nombre o apellido..." class="input-buscar" />
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
   <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="cargarUsuarios(1)" :disabled="paginaActual === 1" class="btn-pagina">
        «
      </button>
      <button @click="cargarUsuarios(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pagina">
        Anterior
      </button>
      <div class="paginas-numeros">
        <button v-for="p in paginasVisibles" :key="p" @click="cargarUsuarios(p)"
          :class="['btn-num', p === paginaActual ? 'activo' : '']">
          {{ p }}
        </button>
      </div>
      <button @click="cargarUsuarios(paginaActual + 1)" :disabled="paginaActual === totalPaginas" class="btn-pagina">
        Siguiente
      </button>
      <button @click="cargarUsuarios(totalPaginas)" :disabled="paginaActual === totalPaginas" class="btn-pagina">
        »
      </button>
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
import iconoLupa from '@/assets/lupa-buscador.svg'

import { ref, onMounted, computed } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const usuarios = ref([])
const cargando = ref(true)
const mensaje = ref('')
const mensajeExito = ref(true)
const paginaActual = ref(1)
const totalPaginas = ref(1)
const total = ref(0)

const buscar = ref('')
let timeoutBuscar = null

onMounted(async () => {
  await cargarUsuarios()
})

async function cargarUsuarios(pagina = 1) {
  cargando.value = true
  paginaActual.value = pagina

  try {
    const params = { pagina }

    if (buscar.value) {
      params.buscar = buscar.value
    }

    const response = await api.get('/api/auth/listar/', { params })

    usuarios.value = response.data.usuarios || []
    total.value = response.data.total
    totalPaginas.value = response.data.total_paginas
    paginaActual.value = response.data.pagina

  } catch (e) {
    console.error('Error cargando usuarios:', e)
  } finally {
    cargando.value = false
  }
}
//para buscar usuario
function buscarUsuarios() {
  clearTimeout(timeoutBuscar)
  timeoutBuscar = setTimeout(() => {
    cargarUsuarios(1)
  }, 400)
}

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

.toolbar h3 {
  font-size: 1.45em;
  font-weight: 700;
  color: #1a3a6b;
}

.btn-actualizar {
  background: #1a3a6b;
  color: rgb(255, 255, 255);
  font-size: 1.01em;
  font-weight: 600;
  border: none;
  padding: 11px 29px;
  border-radius: 6px;
  cursor: pointer;

}

.btn-actualizar:hover {
  background: #000000;
  color: #ffffff;
}
.btn-actualizar disabled {
  opacity: 0.6;
}

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

/* buscador */
.buscador {
  margin-left: 230px;
  display: flex;
  align-items: flex-end;
}

/* WRAPPER */
.buscador-input {
  position: relative;
  width: 100%;
  max-width: 250px;
}

/* INPUT */
.input-buscar {
  width: 100%;
  padding: 10px 14px 10px 40px;
  border: 1px solid #ecedee;
  border-radius: 8px;
  font-size: 1.04em;
  font-weight: 500;
  background: #fff;
  color: #ec0404;
  outline: none;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.input-buscar:hover {
  border-color: #cbd5e1;
}

.input-buscar:focus {
  border-color: #1a3a6b;
}

/* ICONO IMG */
.icono-buscar {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  opacity: 0.6;
  pointer-events: none;
}

/* PLACEHOLDER */
.input-buscar::placeholder {
  color: #9ca3af;
  font-size: 0.9em;
}
/* estilos de paginacion */
.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-pagina {
  background: #026d5f;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: 0.2s;
}

.btn-pagina:hover:not(:disabled) {
  background: #01c5ab;
}

.btn-pagina:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paginas-numeros {
  display: flex;
  gap: 4px;
}

.btn-num {
  background: #026d5f;
  color:#ffffff;
  border: none;
  padding: 7px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: 0.2s;
}

.btn-num:hover {
  background: #01c5ab;
}

.btn-num.activo {
  background: #00f483;
  color: white;
  font-weight: bold;
}


/* para el responsive */
@media (max-width: 768px) {

  /* Toolbar en columna */
  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .toolbar h3 {
    font-size: 1.5em;
    text-align: left;
  }

  /* Buscador full ancho */
  .buscador {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }

  .buscador-input {
    max-width: 100%;
  }

  .input-buscar {
    width: 100%;
    font-size: 0.95em;
  }

  /* Botón actualizar full ancho */
  .btn-actualizar {
    width: 100%;
    text-align: center;
    padding: 10px;
  }

  /* Tabla scroll horizontal */
  .tabla-container {
    overflow-x: auto;
  }

  .tabla {
    min-width: 900px; /* importante para no romper columnas */
  }

  /* Ajustes de acciones */
  .acciones {
    gap: 3px;
  }

  .btn-accion img {
    width: 16px;
    height: 16px;
  }

  /* Select rol más compacto */
  .select-rol {
    font-size: 0.75rem;
    padding: 3px 6px;
  }

  /* Paginación tipo scroll horizontal */
  .paginacion {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 10px;
  }
  .paginas-numeros {
    display: flex;
    gap: 6px;
  }
  .paginacion button {
    flex-shrink: 0;
    padding: 5px 8px;
    font-size: 0.8rem;
  }
  .btn-extremo {
    display: none;
  }
}


</style>