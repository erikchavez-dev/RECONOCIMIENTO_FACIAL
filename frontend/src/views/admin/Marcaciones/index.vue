<!-- MarcacionesView.vue — Marcaciones con vista por período -->
<template>
  <AdminLayout titulo="Marcaciones">

    <div class="toolbar">
      <div>
        <h3>Marcaciones</h3>
        <p class="fecha">{{ fechaHoy }}</p>
      </div>
      <div class="toolbar-right">
        <!-- Tabs de período -->
        <div class="periodo-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.valor"
            :class="['tab-btn', { activo: periodoActivo === tab.valor }]"
            @click="cambiarPeriodo(tab.valor)"
            :disabled="cargando"
          >
            {{ tab.label }}
          </button>
        </div>
        <button @click="cargar" :disabled="cargando" class="btn-actualizar">
          {{ cargando ? '...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <!-- ESTADÍSTICAS rápidas del período -->
    <div class="stats-row" v-if="!cargando && stats">
      <div class="stat-chip">
        <span class="stat-num">{{ stats.total }}</span>
        <span class="stat-lbl">Total</span>
      </div>
      <div class="stat-chip verde">
        <span class="stat-num">{{ stats.entradas }}</span>
        <span class="stat-lbl">Entradas</span>
      </div>
      <div class="stat-chip azul">
        <span class="stat-num">{{ stats.salidas }}</span>
        <span class="stat-lbl">Salidas</span>
      </div>
      <div class="stat-chip amarillo">
        <span class="stat-num">{{ stats.tardanzas }}</span>
        <span class="stat-lbl">Tardanzas</span>
      </div>
      <div class="stat-chip gris">
        <span class="stat-num">{{ stats.puntuales }}</span>
        <span class="stat-lbl">Puntuales</span>
      </div>
    </div>

    <!-- TABLA -->
    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando marcaciones...</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Trabajador</th>
            <th>DNI</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Fecha y Hora</th>
            <th>Dispositivo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="marcaciones.length === 0">
            <td colspan="6" class="vacio">No hay marcaciones en este período</td>
          </tr>
          <tr v-for="m in itemsPagina" :key="m.id">
            <td class="td-nombre">{{ m.trabajador_nombre }}</td>
            <td>{{ m.dni }}</td>
            <td>
              <span :class="['badge', m.tipo === 'ENTRADA' ? 'badge-entrada' : 'badge-salida']">
                {{ m.tipo }}
              </span>
            </td>
            <td>
              <span v-if="m.estado" :class="['badge', m.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']">
                {{ m.estado }}
              </span>
              <span v-else class="sin-estado">—</span>
            </td>
            <td class="td-fecha">{{ formatearFechaHora(m.fecha) }}</td>
            <td class="td-dispositivo">{{ m.dispositivo }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginador -->
    <PaginadorUI
      :pagina-actual="paginaActual"
      :total-paginas="totalPaginas"
      :paginas-visibles="paginasVisibles"
      @ir="irA"
    />

    <!-- Pie: total de registros -->
    <div v-if="!cargando && marcaciones.length > 0" class="pie-tabla">
      {{ marcaciones.length }} registro{{ marcaciones.length !== 1 ? 's' : '' }} —
      mostrando {{ itemsPagina.length }} en esta página
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout  from '@/components/AdminLayout.vue'
import PaginadorUI  from '@/components/ui/PaginadorUI.vue'
import { usePaginacion } from '@/composables/usePaginacion'
import api from '@/services/api'

const marcaciones   = ref([])
const cargando      = ref(true)
const periodoActivo = ref('hoy')

// Paginación cliente: 25 filas por página, sobre el array completo
const { paginaActual, totalPaginas, paginasVisibles, itemsPagina, resetear, irA } =
  usePaginacion(marcaciones, 7)

const tabs = [
  { valor: 'hoy',    label: 'Hoy'    },
  { valor: 'semana', label: 'Semana' },
  { valor: 'mes',    label: 'Mes'    },
]

const fechaHoy = computed(() =>
  new Date().toLocaleDateString('es-PE', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric'
  })
)

// Estadísticas calculadas sobre el array completo (no solo la página)
const stats = computed(() => {
  if (!marcaciones.value.length) return null
  const entradas = marcaciones.value.filter(m => m.tipo === 'ENTRADA')
  const salidas  = marcaciones.value.filter(m => m.tipo === 'SALIDA')
  return {
    total:     marcaciones.value.length,
    entradas:  entradas.length,
    salidas:   salidas.length,
    puntuales: entradas.filter(m => m.estado === 'PUNTUAL').length,
    tardanzas: entradas.filter(m => m.estado === 'TARDANZA').length,
  }
})

function getRango(periodo) {
  const hoy   = new Date()
  const toISO = d => d.toLocaleDateString('en-CA')

  if (periodo === 'hoy')
    return { inicio: toISO(hoy), fin: toISO(hoy) }

  if (periodo === 'semana') {
    const lunes = new Date(hoy)
    lunes.setDate(hoy.getDate() - ((hoy.getDay() + 6) % 7))
    return { inicio: toISO(lunes), fin: toISO(hoy) }
  }

  if (periodo === 'mes') {
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    return { inicio: toISO(primerDia), fin: toISO(hoy) }
  }
}

// Ordena siempre descendente: más reciente primero
function ordenarDescendente(lista) {
  return [...lista].sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
}

async function cargar() {
  cargando.value = true
  resetear()
  try {
    if (periodoActivo.value === 'hoy') {
      const res = await api.get('/api/marcaciones/hoy/')
      marcaciones.value = ordenarDescendente(res.data.marcaciones || [])
    } else {
      const { inicio, fin } = getRango(periodoActivo.value)
      const res = await api.get('/api/marcaciones/reporte/', {
        params: { fecha_inicio: inicio, fecha_fin: fin }
      })
      marcaciones.value = ordenarDescendente(res.data.marcaciones || [])
    }
  } catch (e) {
    console.error('Error cargando marcaciones:', e)
    marcaciones.value = []
  } finally {
    cargando.value = false
  }
}

async function cambiarPeriodo(nuevo) {
  if (periodoActivo.value === nuevo || cargando.value) return
  periodoActivo.value = nuevo
  await cargar()
}

function formatearFechaHora(fecha) {
  return new Date(fecha).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(cargar)
</script>


<style scoped src="./style.css"></style>