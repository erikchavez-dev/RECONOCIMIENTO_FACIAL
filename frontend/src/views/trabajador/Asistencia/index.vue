<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <!-- HEADER -->
    <AppHeader />

    <main class="content">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Asistencia</h2>
      </div>

      <div class="filtros-card">
        <div class="filtros">
          <div class="campo">
            <label>Desde</label>
            <input v-model="fechaInicio" type="date" />
          </div>
          <div class="campo">
            <label>Hasta</label>
            <input v-model="fechaFin" type="date" />
          </div>
          <button @click="cargar" :disabled="cargando" class="btn-buscar">
            {{ cargando ? 'Cargando...' : 'Buscar' }}
          </button>
        </div>
      </div>

      <div v-if="datos" class="resumen-grid">
        <div class="resumen-card verde">
          <div class="res-icon"></div>
          <span class="res-valor">{{ datos.resumen.asistencias }}</span>
          <span class="res-label">Asistencias</span>
        </div>
        <div class="resumen-card amarillo">
          <div class="res-icon"></div>
          <span class="res-valor">{{ datos.resumen.tardanzas }}</span>
          <span class="res-label">Tardanzas</span>
        </div>
        <div class="resumen-card rojo">
          <div class="res-icon"></div>
          <span class="res-valor">{{ datos.resumen.faltas }}</span>
          <span class="res-label">Faltas</span>
        </div>
        <div class="resumen-card azul">
          <div class="res-icon"></div>
          <span class="res-valor">{{ datos.resumen.total_dias }}</span>
          <span class="res-label">Días registrados</span>
        </div>
      </div>

      <div v-if="datos" class="tabla-card">
        <div v-if="datos.dias.length === 0" class="vacio">
          No hay registros en este período
        </div>
        <table v-else class="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Entrada</th>
              <th>Salida</th>
              <th>Tiempo trabajado</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dia in itemsPagina" :key="dia.fecha">
              <td class="celda-fecha">
                <span class="dia-semana">{{ dia.dia_semana }}</span>
                <span class="dia-fecha-txt">{{ formatearFechaCorta(dia.fecha) }}</span>
              </td>
              <td>
                <div v-if="dia.entrada_hora" class="celda-marcacion">
                  <span :class="['chip', dia.entrada_estado === 'PUNTUAL' ? 'chip-p' : 'chip-t']">
                    {{ dia.entrada_estado === 'PUNTUAL' ? 'P' : 'T' }}
                  </span>
                  <span class="hora-texto">{{ dia.entrada_hora }}</span>
                </div>
                <span v-else class="sin-dato">—</span>
              </td>
              <td>
                <div v-if="dia.salida_hora" class="celda-marcacion">
                  <span class="chip chip-s">S</span>
                  <span class="hora-texto">{{ dia.salida_hora }}</span>
                </div>
                <span v-else class="sin-dato">—</span>
              </td>
              <td>
                <span v-if="dia.tiempo_trabajado" class="tiempo-trabajado">
                  {{ dia.tiempo_trabajado }}
                </span>
                <span v-else class="sin-dato">—</span>
              </td>
              <td>
                <span :class="['resultado-chip', claseResultado(dia.resultado)]">
                  {{ dia.resultado }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- PAGINACIÓN -->
      <div class="paginacion" v-if="datos && totalPaginas > 1">

        <button @click="irA(1)" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">
          «
        </button>

        <button @click="irA(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pagina">
          ‹ Anterior
        </button>

        <div class="paginas-numeros">
          <button v-for="p in paginasVisibles" :key="p" @click="irA(p)"
            :class="['btn-num', p === paginaActual ? 'activo' : '']">
            {{ p }}
          </button>
        </div>

        <button @click="irA(paginaActual + 1)" :disabled="paginaActual === totalPaginas" class="btn-pagina">
          Siguiente ›
        </button>

        <button @click="irA(totalPaginas)" :disabled="paginaActual === totalPaginas" class="btn-pagina btn-extremo">
          »
        </button>

      </div>
      <div v-if="cargando" class="cargando">Cargando...</div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuth } from '@/composables/useAuth'
import { useFecha } from '@/composables/useFecha'
import { usePaginacion } from '@/composables/usePaginacion'
import AppHeader from '@/components/layout/AppHeader.vue'
import api from '@/services/api'

const theme = useThemeStore()
const { auth, handleLogout } = useAuth()
const { formatearFechaCorta, claseResultado } = useFecha()

const datos = ref(null)
const cargando = ref(false)

// Días ordenados descendente
const diasOrdenados = computed(() =>
  datos.value
    ? [...datos.value.dias].sort((a, b) => b.fecha.localeCompare(a.fecha))
    : []
)

// Paginación
const {
  paginaActual,
  totalPaginas,
  paginasVisibles,
  itemsPagina,
  resetear,
  irA
} = usePaginacion(diasOrdenados, 8)

const hoy = new Date()
const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)

// Inicializar vacíos, no con el día 1
const fechaInicio = ref('')
const fechaFin    = ref('')

onMounted(() => cargar())

async function cargar() {
  cargando.value = true
  resetear()
  try {
    // Solo enviar fechas si el usuario las eligió manualmente
    const params = {}
    if (fechaInicio.value && fechaFin.value) {
      params.fecha_inicio = fechaInicio.value
      params.fecha_fin    = fechaFin.value
    }

    const response = await api.get('/api/marcaciones/asistencia/', { params })
    datos.value = response.data

    // Rellenar los inputs con el período que devolvió el backend
    if (datos.value?.periodo) {
      fechaInicio.value = datos.value.periodo.inicio
      fechaFin.value    = datos.value.periodo.fin
    }
  } catch (e) {
    console.error('Error cargando asistencia:', e)
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped src="./style.css"></style>