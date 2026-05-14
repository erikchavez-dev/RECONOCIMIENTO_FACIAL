<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <AppHeader />

    <main class="content">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Historial de Marcaciones</h2>
        <span class="subtitulo">Mostrando últimos 50 registros</span>
      </div>

      <div v-if="cargando" class="estado-msg">
        <span class="estado-spinner"><img :src="relojArena" class="reloj-arena" alt="Reloj"/></span>
        Cargando historial...
      </div>

      <div v-else-if="error" class="error-box">{{ error }}</div>

      <div v-else-if="marcaciones.length > 0" class="tabla-wrapper">
        <table class="historia-tabla">
          <thead>
            <tr>
              <th>Fecha de Registro</th>
              <th>Hora Exacta</th>
              <th>Tipo</th>
              <th>Estado del Marcaje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in itemsPagina" :key="m.id">

              <td class="col-fecha">{{ formatearFecha(m.fecha) }}</td>

              <td class="col-hora">{{ formatearHora(m.fecha) }}</td>

              <td class="col-tipo">
                <span class="type-pill" :class="tipoPillClass(m.tipo)">
                  {{ formatearTipo(m.tipo) }}
                </span>
              </td>

              <td class="col-estado">
                <div class="status-indicator">
                  <span class="dot" :class="estadoDotClass(m.estado, m.tipo)"></span>
                  <span :class="estadoTextoClass(m.estado, m.tipo)">{{ formatearEstado(m.estado, m.tipo) }}</span>
                </div>
              </td>

            </tr>
          </tbody>
        </table>

        <div class="footer-tabla">
          <span class="info-pagina">Página {{ paginaActual }} de {{ totalPaginas }}</span>

          <div class="paginacion" v-if="totalPaginas > 1">
            <button @click="paginaActual = 1" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">«</button>
            <button @click="paginaActual--" :disabled="paginaActual === 1" class="btn-pagina">‹ Anterior</button>
            <div class="paginas-numeros">
              <button
                v-for="p in paginasVisibles"
                :key="p"
                @click="paginaActual = p"
                :class="['btn-num', p === paginaActual ? 'activo' : '']"
              >{{ p }}</button>
            </div>
            <button @click="paginaActual++" :disabled="paginaActual === totalPaginas" class="btn-pagina">Siguiente ›</button>
            <button @click="paginaActual = totalPaginas" :disabled="paginaActual === totalPaginas" class="btn-pagina btn-extremo">»</button>
          </div>
        </div>
      </div>

      <div v-else class="estado-msg">
        <span class="estado-emoji"></span>
        <span>No hay marcaciones registradas</span>
      </div>
    </main>
  </div>
</template>

<script setup>
import relojArena from '@/assets/reloj-de-arena.webp'

import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuth } from '@/composables/useAuth'
import AppHeader from '@/components/layout/AppHeader.vue'
import { usePaginacion } from '@/composables/usePaginacion'
import api from '@/services/api'

const theme = useThemeStore()
const { auth, handleLogout } = useAuth()

const marcaciones = ref([])
const cargando = ref(true)
const error = ref('')

const {
  paginaActual,
  totalPaginas,
  paginasVisibles,
  itemsPagina,
} = usePaginacion(marcaciones, 6)

onMounted(async () => {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const response = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    marcaciones.value = response.data
  } catch (e) {
    error.value = 'Error al cargar el historial'
  } finally {
    cargando.value = false
  }
})

function formatearFecha(fecha) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleDateString('es-PE', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).replace(/^\w/, c => c.toUpperCase())
}

function formatearHora(fecha) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleTimeString('es-PE', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatearTipo(tipo) {
  if (!tipo) return '—'
  if (tipo.includes('ENTRADA')) return 'Entrada'
  if (tipo.includes('SALIDA')) return 'Salida'
  return tipo
}

function tipoPillClass(tipo = '') {
  if (tipo.includes('ENTRADA')) return 'pill-entrada'
  if (tipo.includes('SALIDA')) return 'pill-salida'
  return ''
}

function estadoDotClass(estado = '', tipo = '') {
  if (estado === 'PUNTUAL') return 'dot-puntual'
  if (tipo?.includes('SALIDA')) return 'dot-puntual'
  return 'dot-fuera'
}

function estadoTextoClass(estado = '', tipo = '') {
  if (estado === 'PUNTUAL') return 'texto-puntual'
  if (tipo?.includes('SALIDA')) return 'texto-puntual'
  return 'texto-fuera'
}

function formatearEstado(estado = '', tipo = '') {
  if (tipo?.includes('SALIDA')) return '✓ Día cumplido'
  if (estado === 'PUNTUAL') return 'Puntual'
  return estado || 'Fuera de Horario'
}
</script>

<style scoped src="./style.css"></style>