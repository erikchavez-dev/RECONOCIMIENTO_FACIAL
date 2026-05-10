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

<style scoped>
/* FILTROS */
.filtros-card {
  background: var(--bg-panel, white);
  border-radius: 10px;
  padding: 16px 20px;
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
  margin-bottom: 16px;
  border: 1px solid var(--border, #e5e7eb);
}

.filtros {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.campo { display: flex; flex-direction: column; gap: 4px; }
.campo-buscar { flex: 1; min-width: 200px; }

.campo label {
  font-size: 1em;
  font-weight: 600;
  color: var(--text-accent, #1a3a6b);
}

.campo input, .sel-accion {
  padding: 8px 10px;
  border: 1px solid var(--border, #ddd);
  border-radius: 6px;
  font-size: 0.9em;
  background: var(--bg-input, white);
  color: var(--text-primary, #111);
}

.campo input:focus, .sel-accion:focus {
  outline: none;
  border-color: var(--border-focus, #1a3a6b);
}

.input-buscar { width: 100%; }

.btn-limpiar {
  padding: 9px 15px;
  background: #ff0000;
  border: 1px solid var(--border, #ddd);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  color: #fff;
  white-space: nowrap;
}

.btn-limpiar:hover {
  background: #cc0202;
  color: #ffffff;
  border-color: #fecaca;
}

.btn-actualizar {
  background: #1a3a6b;
  color: rgb(255, 255, 255);
  font-size: 1em;
  font-weight: 600;
  border: none;
  padding: 9px 15px;
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

/* INFO TOTAL */
.info-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.82rem;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 10px;
  padding: 0 4px;
}

/* TABLA */
.tabla-container {
  background: var(--bg-panel, white);
  border-radius: 10px;
  overflow: auto;
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
  border: 1px solid var(--border, #e5e7eb);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.84rem; }

.tabla th {
  background: var(--bg-table-head, #1a3a6b);
  color: white;
  padding: 11px 14px;
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}

.tabla td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border, #f0f0f0);
  color: var(--text-primary, #333);
  vertical-align: top;
}

.tabla tr:hover { background: var(--bg-hover, #f8fafc); }
.tabla tr:last-child td { border-bottom: none; }

.celda-usuario { font-weight: 600; white-space: nowrap; }
.celda-fecha   { white-space: nowrap; font-size: 0.8rem; color: var(--text-secondary, #666); }
.celda-ip      { font-family: monospace; font-size: 0.78rem; color: var(--text-muted, #9ca3af); }
.descripcion   { max-width: 320px; font-size: 0.8rem; color: var(--text-secondary, #555); line-height: 1.4; }

/* BADGES */
.badge {
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
  display: inline-block;
}
.badge-verde   { background: var(--bg-badge-ok,   #dcfce7); color: var(--text-badge-ok,   #16a34a); }
.badge-rojo    { background: var(--bg-badge-err,  #fee2e2); color: var(--text-badge-err,  #dc2626); }
.badge-azul    { background: var(--bg-badge-info, #dbeafe); color: var(--text-badge-info, #1d4ed8); }
.badge-naranja { background: #ffedd5; color: #ea580c; }
.badge-amarillo{ background: var(--bg-badge-warn, #fef9c3); color: var(--text-badge-warn, #ca8a04); }
.badge-gris    { background: #f3f4f6; color: #6b7280; }

.vacio {
  text-align: center;
  color: var(--text-muted, #9ca3af);
  padding: 48px !important;
  font-size: 0.9rem;
}

/* CARGANDO */
.cargando {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px;
  color: var(--text-muted, #9ca3af);
  font-size: 0.9rem;
}
.spinner {
  width: 24px; height: 24px;
  border: 3px solid var(--border, #e5e7eb);
  border-top-color: var(--accent, #1a3a6b);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
/* PAGINACIÓN */
.paginacion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  flex-wrap: wrap;

}
.paginacion button {
  background: #026d5f;
  flex-shrink: 0;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-pagina {
  padding: 7px 14px;
  background: var(--bg-panel, white);
  color: var(--text-accent, #1a3a6b);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 0.15s;
  white-space: nowrap;
}

.btn-pagina:hover:not(:disabled) {
  background: #01c5ab;
}

.btn-pagina:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-extremo {
  font-size: 0.75rem;
  padding: 7px 10px;
}

.paginas-numeros {
  display: flex;
  gap: 4px;
}


.btn-num.activo {
  background: #00f483;
  font-weight: bold;
}
.btn-num:hover {
  background: #01c5ab;
}


.pagina-info {
  font-weight: 600;
  color: var(--text-accent, #1a3a6b);
}


/* para el responsive */
@media (max-width: 768px) {

  .paginacion {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;

    flex-wrap: nowrap;     /* 🔥 igual que trabajadores */
    overflow-x: auto;      /* 🔥 scroll horizontal */
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


}

</style>