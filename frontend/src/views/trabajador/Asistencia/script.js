import { ref, computed, onMounted } from 'vue'
import { useThemeStore }   from '@/stores/theme'
import { useAuth }         from '@/composables/useAuth'
import { useFecha }        from '@/composables/useFecha'
import { usePaginacion }   from '@/composables/usePaginacion'
import AppHeader           from '@/components/layout/AppHeader.vue'
import api                 from '@/services/api'

export default {
  components: { AppHeader },
  setup() {
    const theme                  = useThemeStore()
    const { auth, handleLogout } = useAuth()
    const { formatearFechaCorta, claseResultado } = useFecha()

    const datos    = ref(null)
    const cargando = ref(false)

    // Días ordenados descendente: más reciente primero
    const diasOrdenados = computed(() =>
      datos.value
        ? [...datos.value.dias].sort((a, b) => b.fecha.localeCompare(a.fecha))
        : []
    )

    // Paginación cliente: 20 días por página
    const { paginaActual, totalPaginas, paginasVisibles, itemsPagina, resetear, irA } =
      usePaginacion(diasOrdenados, 8)

    const hoy       = new Date()
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    const fechaInicio = ref(primerDia.toISOString().split('T')[0])
    const fechaFin    = ref(hoy.toISOString().split('T')[0])

    onMounted(() => cargar())

    async function cargar() {
      cargando.value = true
      resetear()
      try {
        const response = await api.get('/api/marcaciones/asistencia/', {
          params: { fecha_inicio: fechaInicio.value, fecha_fin: fechaFin.value }
        })
        datos.value = response.data
      } catch (e) {
        console.error('Error cargando asistencia:', e)
      } finally {
        cargando.value = false
      }
    }

    return {
      auth, theme,
      datos, cargando,
      fechaInicio, fechaFin,
      cargar,
      formatearFechaCorta,
      claseResultado,
      handleLogout,
      // paginación
      paginaActual, totalPaginas, paginasVisibles, itemsPagina, irA,
    }
  }
}