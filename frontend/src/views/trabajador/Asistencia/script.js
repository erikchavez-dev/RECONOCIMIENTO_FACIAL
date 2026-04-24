import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna   from '@/assets/icon-luna.svg'
import iconoSol    from '@/assets/icon-sol.svg'

import { ref, onMounted } from 'vue'
import { useRouter }      from 'vue-router'
import { useAuthStore }   from '@/stores/auth'
import { useThemeStore }  from '@/stores/theme'
import api                from '@/services/api'

export default {
  setup() {
    const router = useRouter()
    const auth   = useAuthStore()
    const theme  = useThemeStore()

    const datos    = ref(null)
    const cargando = ref(false)

    const hoy       = new Date()
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    const fechaInicio = ref(primerDia.toISOString().split('T')[0])
    const fechaFin    = ref(hoy.toISOString().split('T')[0])

    onMounted(() => cargar())

    async function cargar() {
      cargando.value = true
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

    function formatearFechaCorta(fechaStr) {
      const [y, m, d] = fechaStr.split('-')
      return `${d}/${m}/${y}`
    }

    function claseResultado(resultado) {
      if (resultado === 'ASISTIÓ')    return 'res-asistio'
      if (resultado === 'TARDANZA')   return 'res-tardanza'
      if (resultado === 'SIN SALIDA') return 'res-sin-salida'
      return 'res-falta'
    }

    async function handleLogout() {
      await auth.logout()
      router.push('/login')
    }

    return {
      iconoPerfil, iconoLuna, iconoSol,
      auth, theme,
      datos, cargando,
      fechaInicio, fechaFin,
      cargar,
      formatearFechaCorta,
      claseResultado,
      handleLogout,
    }
  }
}