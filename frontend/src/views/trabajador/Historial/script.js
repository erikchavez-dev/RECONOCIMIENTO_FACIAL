import relojArena from '@/assets/reloj-de-arena.webp'

import { ref, onMounted } from 'vue'
import { useThemeStore }  from '@/stores/theme'
import { useAuth }        from '@/composables/useAuth'
import AppHeader          from '@/components/layout/AppHeader.vue'
import { usePaginacion }  from '@/composables/usePaginacion'
import api                from '@/services/api'

export default {
  components: { AppHeader },
  setup() {
    const theme                  = useThemeStore()
    const { auth, handleLogout } = useAuth()

    const marcaciones = ref([])
    const cargando    = ref(true)
    const error       = ref('')
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
        weekday: 'long', day: '2-digit', month: 'long', year: 'numeric'
      }).replace(/^\w/, c => c.toUpperCase())
    }

    function formatearHora(fecha) {
      if (!fecha) return '—'
      return new Date(fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit'
      })
    }

    function formatearTipo(tipo) {
      if (!tipo) return '—'
      if (tipo.includes('ENTRADA')) return 'Entrada'
      if (tipo.includes('SALIDA'))  return 'Salida'
      return tipo
    }

    function tipoPillClass(tipo = '') {
      if (tipo.includes('ENTRADA')) return 'pill-entrada'
      if (tipo.includes('SALIDA'))  return 'pill-salida'
      return ''
    }

    function estadoDotClass(estado = '') {
      if (estado === 'PUNTUAL') return 'dot-puntual'
      return 'dot-fuera'
    }

    function estadoTextoClass(estado = '') {
      if (estado === 'PUNTUAL') return 'texto-puntual'
      return 'texto-fuera'
    }

    return {
      relojArena,
      auth, theme,
      marcaciones, cargando, error,
      handleLogout,
      paginaActual,
      totalPaginas,
      paginasVisibles,
      itemsPagina,
      formatearFecha,
      formatearHora,
      formatearTipo,
      tipoPillClass,
      estadoDotClass,
      estadoTextoClass,
    }
  }
}