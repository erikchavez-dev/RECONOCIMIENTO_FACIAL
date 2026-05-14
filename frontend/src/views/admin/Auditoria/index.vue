<template>
  <AdminLayout titulo="Auditoría">

    <!-- FILTROS -->
    <div class="filtros-card">
      <div class="filtros">
        <div class="campo campo-buscar">
          <label>Buscar</label>
          <input
            v-model="buscar"
            @input="buscarConDelay"
            type="text"
            placeholder="Usuario, acción, descripción..."
            class="input-buscar"
          />
        </div>

        <div class="campo">
          <label>Tipo de acción</label>
          <select v-model="accionFiltro" @change="cargarAuditoria(1)" class="sel-accion">
            <option value="">Todas</option>
            <option value="LOGIN">Login</option>
            <option value="MARCACION">Marcación</option>
            <option value="VERIFICACION">Verificación facial</option>
            <option value="CREAR">Crear</option>
            <option value="ELIMINAR">Eliminar</option>
            <option value="CAMBIO">Cambio</option>
            <option value="CONFIGURACION">Configuración</option>
            <option value="BLOQUEAR">Bloqueo</option>
            <option value="DESBLOQUEAR">Desbloqueo</option>
            <option value="RESETEAR">Resetear</option>
            <option value="EMBEDDING">Embedding</option>
          </select>
        </div>

        <div class="campo">
          <label>Desde</label>
          <input v-model="fechaInicio" @change="cargarAuditoria(1)" type="date" />
        </div>

        <div class="campo">
          <label>Hasta</label>
          <input v-model="fechaFin" @change="cargarAuditoria(1)" type="date" />
        </div>

        <button @click="limpiarFiltros" class="btn-limpiar">✕ Limpiar</button>
        <button @click="cargarAuditoria(paginaActual)" class="btn-actualizar">↻ Actualizar</button>
      </div>
    </div>

    <!-- INFO TOTAL -->
    <div class="info-total" v-if="!cargando">
      <span>{{ total }} registros encontrados</span>
      <span class="pagina-info">Página {{ paginaActual }} de {{ totalPaginas }}</span>
    </div>

    <!-- TABLA -->
    <div class="tabla-container">
      <div v-if="cargando" class="cargando">
        <div class="spinner"></div>
        Cargando...
      </div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Acción</th>
            <th>Descripción</th>
            <th>Fecha</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="auditorias.length === 0">
            <td colspan="5" class="vacio">No hay registros con estos filtros</td>
          </tr>
          <tr v-for="a in auditorias" :key="a.id">
            <td class="celda-usuario">{{ a.usuario_nombre }}</td>
            <td>
              <span :class="['badge', getBadgeClass(a.accion)]">
                {{ a.accion }}
              </span>
            </td>
            <td class="descripcion">{{ a.descripcion }}</td>
            <td class="celda-fecha">{{ formatearFecha(a.fecha) }}</td>
            <td class="celda-ip">{{ a.ip }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PAGINACIÓN -->
    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="cargarAuditoria(1)" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">«</button>
      <button @click="cargarAuditoria(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pagina">‹ Anterior</button>

      <div class="paginas-numeros">
        <button
          v-for="p in paginasVisibles"
          :key="p"
          @click="cargarAuditoria(p)"
          :class="['btn-num', p === paginaActual ? 'activo' : '']"
        >{{ p }}</button>
      </div>

      <button @click="cargarAuditoria(paginaActual + 1)" :disabled="paginaActual === totalPaginas" class="btn-pagina">Siguiente ›</button>
      <button @click="cargarAuditoria(totalPaginas)" :disabled="paginaActual === totalPaginas" class="btn-pagina btn-extremo">»</button>
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const auditorias   = ref([])
const cargando     = ref(true)
const paginaActual = ref(1)
const totalPaginas = ref(1)
const total        = ref(0)

const buscar      = ref('')
const accionFiltro = ref('')
const fechaInicio  = ref('')
const fechaFin     = ref('')

let timeoutBuscar = null

onMounted(() => cargarAuditoria(1))

async function cargarAuditoria(pagina = 1) {
  cargando.value = true
  paginaActual.value = pagina
  try {
    const params = { pagina }
    if (buscar.value)       params.buscar       = buscar.value
    if (accionFiltro.value) params.accion       = accionFiltro.value
    if (fechaInicio.value)  params.fecha_inicio = fechaInicio.value
    if (fechaFin.value)     params.fecha_fin    = fechaFin.value

    const response = await api.get('/api/auditoria/', { params })
    auditorias.value   = response.data.auditorias
    total.value        = response.data.total
    totalPaginas.value = response.data.total_paginas
    paginaActual.value = response.data.pagina
  } catch (e) {
    console.error('Error cargando auditoría:', e)
  } finally {
    cargando.value = false
  }
}

function buscarConDelay() {
  clearTimeout(timeoutBuscar)
  timeoutBuscar = setTimeout(() => cargarAuditoria(1), 400)
}

function limpiarFiltros() {
  buscar.value       = ''
  accionFiltro.value = ''
  fechaInicio.value  = ''
  fechaFin.value     = ''
  cargarAuditoria(1)
}

// Mostrar máximo 5 páginas numeradas centradas en la actual
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

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function getBadgeClass(accion) {
  if (accion.includes('LOGIN_EXITOSO') || accion.includes('CREAR') || accion.includes('REGISTRAR')) return 'badge-verde'
  if (accion.includes('LOGIN_FALLIDO') || accion.includes('ELIMINAR') || accion.includes('FALLIDO')) return 'badge-rojo'
  if (accion.includes('MARCACION'))    return 'badge-azul'
  if (accion.includes('VERIFICACION')) return 'badge-naranja'
  if (accion.includes('CAMBIO') || accion.includes('CONFIGURACION') || accion.includes('RESETEAR')) return 'badge-amarillo'
  if (accion.includes('BLOQUEAR') || accion.includes('DESBLOQUEAR')) return 'badge-naranja'
  if (accion.includes('EMBEDDING'))    return 'badge-azul'
  return 'badge-gris'
}
</script>

<style scoped src="./style.css"></style>